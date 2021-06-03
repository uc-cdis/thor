from fastapi import FastAPI
from . import logger

app = FastAPI()


@app.get("/")
async def root():
    logger.debug("Starting Thor...")
    return {"message": "Hello World"}
