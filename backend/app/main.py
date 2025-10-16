from fastapi import FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.utils.jwt_handler import verify_token
from app.routes import auth as auth_routes
from app.routes import monitor as monitor_routes
from app.routes import anomaly as anomaly_routes
from app.routes import defense as defense_routes
from app.database import init_db, get_db
from app.utils.monitor import collect_system_metrics
from app.utils.ml_model import predict_anomaly


def create_app() -> FastAPI:
    app = FastAPI(title="SentinelGuard AI", version="0.1.0")

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

    def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)):
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
        try:
            verify_token(credentials.credentials)
        except Exception:
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
        await db.anomaly_logs.insert_one({"metrics": metrics, **res})
    except Exception:
        pass
