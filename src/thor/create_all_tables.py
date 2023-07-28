from sqlalchemy import MetaData
import sqlalchemy as sa
from dao import config

from thor.dao import models
from sqlalchemy.orm import sessionmaker

engine = sa.create_engine(config.DATABASE_URL)

Session = sessionmaker(bind=engine)

meta = MetaData()


def setup_db_and_create_test_data():
    s = Session()

    # Create tables
    meta.tables = {"releases": models.Release.__table__, "tasks": models.Task.__table__}

    meta.create_all(engine)

    s.commit()
    s.close()


if __name__ == "__main__":
    setup_db_and_create_test_data()
