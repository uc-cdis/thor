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

    # Existing databases may already have the releases table.
    # create_all() does not add new columns to existing tables,
    # so add release_start_time only when it is missing.
    inspector = sa.inspect(engine)

    release_columns = {
        column["name"]
        for column in inspector.get_columns("releases")
    }

    if "release_start_time" not in release_columns:
        with engine.begin() as connection:
            connection.execute(
                sa.text(
                    """
                    ALTER TABLE releases
                    ADD COLUMN release_start_time TIMESTAMP WITH TIME ZONE
                    """
                )
            )

    s.commit()
    s.close()


if __name__ == "__main__":
    setup_db_and_create_test_data()
