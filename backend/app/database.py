import os
import asyncio
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

# Supabase client
try:
    from supabase import create_client  # type: ignore
except Exception:  # pragma: no cover - import error at runtime
    create_client = None  # type: ignore

load_dotenv()


def get_supabase_url() -> Optional[str]:
    return os.getenv("SUPABASE_URL")


def get_supabase_key() -> Optional[str]:
    return os.getenv("SUPABASE_KEY")


class SupabaseCursor:
    """Async iterator that performs a Supabase query when iterated."""

    def __init__(self, client: Any, table: str, filters: Optional[List[tuple]] = None):
        self.client = client
        self.table = table
        self._filters = filters or []
        self._order: Optional[tuple] = None
        self._limit: Optional[int] = None
        self._data: Optional[List[Dict[str, Any]]] = None
        self._idx = 0

    def sort(self, field: str, direction: int):
        self._order = (field, "desc" if direction == -1 else "asc")
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    async def _fetch(self) -> List[Dict[str, Any]]:
        def _sync_query():
            q = self.client.table(self.table).select("*")
            for k, v in self._filters:
                q = q.eq(k, v)
            if self._order:
                q = q.order(self._order[0], desc=(self._order[1] == "desc"))
            if self._limit:
                q = q.limit(self._limit)
            res = q.execute()
            if res.error:
                raise RuntimeError(res.error)
            data = res.data or []
            # normalize id -> _id for compatibility with Mongo-shaped code
            for row in data:
                if isinstance(row, dict) and "id" in row and "_id" not in row:
                    row["_id"] = row["id"]
            return data

        return await asyncio.to_thread(_sync_query)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._data is None:
            self._data = await self._fetch()
        if self._idx >= len(self._data):
            raise StopAsyncIteration
        item = self._data[self._idx]
        self._idx += 1
        return item


class SupabaseTable:
    def __init__(self, client: Any, table: str):
        self.client = client
        self.table = table

    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        def _sync():
            q = self.client.table(self.table).select("*")
            for k, v in query.items():
                # map _id to id if present
                key = "id" if k == "_id" else k
                q = q.eq(key, v)
            res = q.limit(1).execute()
            if res.error:
                raise RuntimeError(res.error)
            out = (res.data[0] if res.data else None)
            if out and isinstance(out, dict) and "id" in out and "_id" not in out:
                out["_id"] = out["id"]
            return out

        return await asyncio.to_thread(_sync)

    class InsertOneResult:
        def __init__(self, inserted_id: Any):
            self.inserted_id = inserted_id

    async def insert_one(self, doc: Dict[str, Any]) -> InsertOneResult:
        def _sync():
            res = self.client.table(self.table).insert(doc).execute()
            if res.error:
                raise RuntimeError(res.error)
            # emulate inserted_id like Mongo
            inserted = res.data[0] if res.data else None
            if inserted and isinstance(inserted, dict) and "id" in inserted and "_id" not in inserted:
                inserted["_id"] = inserted["id"]
            return SupabaseTable.InsertOneResult(inserted.get("id") if inserted else None)

        return await asyncio.to_thread(_sync)

    def find(self, *args, **kwargs) -> SupabaseCursor:
        # support chaining .sort().limit() by returning a cursor
        return SupabaseCursor(self.client, self.table)

    async def delete_one(self, query: Dict[str, Any]) -> Dict[str, Any]:
        def _sync():
            q = self.client.table(self.table).delete()
            for k, v in query.items():
                key = "id" if k == "_id" else k
                q = q.eq(key, v)
            res = q.execute()
            if res.error:
                raise RuntimeError(res.error)
            return {"deleted": True}

        return await asyncio.to_thread(_sync)


class SupabaseDB:
    def __init__(self, client: Any, tables: Optional[List[str]] = None):
        self.client = client
        self._tables = {}
        # lazy table wrapper creation

    def table(self, name: str) -> SupabaseTable:
        if name not in self._tables:
            self._tables[name] = SupabaseTable(self.client, name)
        return self._tables[name]

    def __getattr__(self, item: str) -> SupabaseTable:
        # allow attribute access like db.users
        try:
            return self.table(item)
        except Exception:
            raise AttributeError(item)


_supabase_client: Optional[Any] = None
_db: Optional[SupabaseDB] = None


def init_db() -> SupabaseDB:
    """Initialize Supabase client and return a DB wrapper."""
    global _supabase_client, _db
    if _db is not None:
        return _db

    url = get_supabase_url()
    key = get_supabase_key()
    print(
        f"🔌 Initializing Supabase client (url present: {'yes' if url else 'no'})")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment")
    if create_client is None:
        raise RuntimeError("supabase package is not installed")

    try:
        _supabase_client = create_client(url, key)
        _db = SupabaseDB(_supabase_client)
        print("✅ Supabase client initialized")
        return _db
    except Exception as e:
        print(f"❌ Supabase initialization failed: {e}")
        raise


def get_db() -> SupabaseDB:
    if _db is None:
        return init_db()
    return _db


async def test_connection() -> bool:
    """Simple Supabase connectivity test."""
    try:
        db = get_db()

        def _sync():
            # simple list tables via a small select on pg_catalog if available, else try a ping-like call
            res = db.client.rpc("pg_isready").execute(
            ) if hasattr(db.client, "rpc") else None
            return True

        await asyncio.to_thread(_sync)
        print("✅ Supabase connectivity seems OK")
        return True
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")
        return False


def close_db() -> None:
    global _supabase_client, _db
    # Supabase python client does not require explicit close, but clear refs
    _supabase_client = None
    _db = None
