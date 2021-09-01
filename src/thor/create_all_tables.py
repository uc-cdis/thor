from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
import sqlalchemy as sa
from dao import config
from dao import release_dao
from dao import task_dao
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
    print("creating rows in the releases table...")
    release_dao.manual_create_release(3, "2021.09", "In Progress")
    release_dao.manual_create_release(4, "2021.07", "Completed")

    task_dao.manual_create_task(
        6, "Merge integration branch into stable and tag release", "success", 4
    )
    task_dao.manual_create_task(
        7, "Mark gen3 release as released in JIRA", "success", 4
    )

    task_dao.manual_create_task(1, "Create Release in JIRA", "success", 3)
    task_dao.manual_create_task(2, "Cut integration branch", "success", 3)


if __name__ == "__main__":
    setup_db_and_create_test_data()
