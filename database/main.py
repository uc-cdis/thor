# main.py

import sqlalchemy as sa

from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL
from release_dao import readRelease, getkeys

engine = sa.create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

s = Session()

app = FastAPI()


@app.get("/releases")
async def getall():
    objectString = "{ "
    keylist = getkeys()
    for id in keylist:
        objectString += readRelease(id)
    objectString += " }"

    return {"message": objectString}


s.commit()
s.close()
