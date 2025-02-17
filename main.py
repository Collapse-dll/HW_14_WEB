import redis.asyncio as redis

from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session
from sqlalchemy import text

from src.routes import contacts, auth, users
from src.database.db import get_db
from src.config.config import config

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.on_event("startup")
async def startup():
    r = await redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    return {"message": "Hello World !"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly !"
            )
        return {"message": "Welcome to FastAPI !!!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database !")
