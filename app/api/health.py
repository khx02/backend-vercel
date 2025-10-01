from fastapi import APIRouter, HTTPException

from app.db.client import ping

router = APIRouter()


@router.get("/db")
async def db_health():
    try:
        result = await ping()
        return {"ok": True, "result": result}
    except Exception as e:
        # Surface the exact error to help diagnose Atlas issues in Vercel logs
        raise HTTPException(status_code=503, detail=f"Mongo ping failed: {e}")
