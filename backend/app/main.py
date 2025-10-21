from fastapi import FastAPI
from fastapi import Depends, HTTPException, status, Request
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import PlainTextResponse
import logging
import traceback
from app.utils.jwt_handler import verify_token
from app.routes import auth as auth_routes
from app.routes import monitor as monitor_routes
from app.routes import anomaly as anomaly_routes
from app.routes import defense as defense_routes
from app.database import init_db, get_db
from app.database import close_db
from app.utils.monitor import collect_system_metrics
from app.utils.ml_model import predict_anomaly


def create_app() -> FastAPI:
    app = FastAPI(title="SentinelGuard AI", version="0.1.0")

    # Load environment variables from .env (if present)
    load_dotenv()

    # Logger for unhandled exceptions (writes to the uvicorn error logger)
    logger = logging.getLogger("uvicorn.error")

    @app.exception_handler(Exception)
    async def all_exceptions_handler(request: Request, exc: Exception):
        # Log full traceback to server logs for debugging, keep response generic
        logger.error("Unhandled error on %s %s\n%s", request.method,
                     request.url, traceback.format_exc())
        return PlainTextResponse("Internal Server Error", status_code=500)

    # Initialize database on startup
    @app.on_event("startup")
    async def startup_event():
        print("🚀 Starting SentinelGuard AI...")
        try:
            init_db()  # Initialize MongoDB connection
            print("✅ Database initialized successfully!")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")

        # Log presence of Supabase env vars (mask key)
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        def _mask(s: str | None) -> str:
            if not s:
                return "<missing>"
            if len(s) <= 10:
                return "***"
            return f"{s[:6]}...{s[-4:]}"

        print(f"🔎 SUPABASE_URL: {'set' if supabase_url else 'missing'}")
        print(f"🔒 SUPABASE_KEY: {_mask(supabase_key)}")

    @app.on_event("shutdown")
    async def shutdown_event():
        try:
            close_db()
        except Exception:
            pass

    # CORS for frontend (adjust origins as needed)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
    # Protected routers using simple dependency
    security = HTTPBearer(auto_error=False)

    async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

        token = credentials.credentials
        # Try local JWT verification first
        try:
            verify_token(token)
            return
        except Exception:
            pass

        # If local verification fails, try Supabase token introspection (if client available)
        try:
            db = get_db()
            client = getattr(db, "client", None)
            if client and hasattr(client, "auth"):
                # supabase client may provide get_user or get_user_by_token
                def _get_user():
                    # Try different client methods
                    if hasattr(client.auth, "get_user"):
                        return client.auth.get_user(token)
                    if hasattr(client.auth, "get_user_by_token"):
                        return client.auth.get_user_by_token(token)
                    # older clients may have api.get_user
                    api = getattr(client, "api", None)
                    if api and hasattr(api, "get_user"):
                        return api.get_user(token)
                    # as a last resort, return None
                    return None

                res = await __import__("asyncio").to_thread(_get_user)
                # res could be dict-like or object; accept non-empty as valid
                if res:
                    return
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    app.include_router(monitor_routes.router, prefix="/api/monitor",
                       tags=["monitor"], dependencies=[Depends(require_auth)])
    app.include_router(anomaly_routes.router, prefix="/api/anomaly",
                       tags=["anomaly"], dependencies=[Depends(require_auth)])
    app.include_router(defense_routes.router, prefix="/api/defense",
                       tags=["defense"], dependencies=[Depends(require_auth)])

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()


# Background monitoring task (simple demo)
async def background_monitoring_loop():
    db = get_db()
    try:
        metrics = collect_system_metrics()
        res = predict_anomaly(metrics)
        # Prepare a JSON-serializable payload
        payload = {"metrics": metrics, **res}
        # convert any non-serializable types (like datetime) to strings via jsonable_encoder
        from fastapi.encoders import jsonable_encoder
        payload = jsonable_encoder(payload)
        await db.anomaly_logs.insert_one(payload)
    except Exception:
        pass
