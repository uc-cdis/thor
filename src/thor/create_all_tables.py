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

    # Changes to existing releases table
    with engine.begin() as connection:
        connection.execute(
            sa.text(
                """
                ALTER TABLE releases
                ADD COLUMN IF NOT EXISTS
                release_start_time TIMESTAMP WITH TIME ZONE
                """
            )
        )

        connection.execute(
            sa.text(
                """
                ALTER TABLE releases
                ADD COLUMN IF NOT EXISTS
                release_end_time TIMESTAMP WITH TIME ZONE
                """
            )
        )

    s.commit()
    s.close()


if __name__ == "__main__":
    setup_db_and_create_test_data()
