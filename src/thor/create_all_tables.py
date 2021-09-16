from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
import sqlalchemy as sa
from thor.dao import config
from thor.dao import release_dao
from thor.dao import task_dao
from thor.dao.clear_tables_reseed import create_test_data
from sqlalchemy.orm import sessionmaker

engine = sa.create_engine(config.DATABASE_URL)

Session = sessionmaker(bind=engine)

meta = MetaData()


def setup_db_and_create_test_data():
    s = Session()

    releases = Table(
        "releases",
        meta,
        Column("release_id", Integer, primary_key=True),
        Column("version", String),
        Column("result", String),
    )

    tasks = Table(
        "tasks",
        meta,
        Column("task_id", Integer, primary_key=True),
        Column("task_name", String),
        Column("status", String),
        Column("release_id", Integer, ForeignKey("releases.release_id")),
    )

    meta.create_all(engine)

    s.commit()
    s.close()

    # Add dummy release entries for testing purposes
    print("Creating entires in Releases and Tasks tables...")

    create_test_data()


if __name__ == "__main__":
    setup_db_and_create_test_data()
