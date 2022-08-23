import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from thor.dao import config
from thor.dao import release_dao
from thor.dao import task_dao

from thor.dao.release_dao import get_release_keys, delete_release
from thor.dao.task_dao import get_task_keys, delete_task

engine = sa.create_engine(config.DATABASE_URL)

Session = sessionmaker(bind=engine)


def clear_tables():
    """ You know, it hurts me to write this code. 
    Uses release_dao and task_dao's built-in delete
    functions to delete release / task objects one by one. 
    """
    s = Session()

    task_keys = get_task_keys()
    for task_key in task_keys:
        delete_task(task_key)

    release_keys = get_release_keys()
    for release_key in release_keys:
        delete_release(release_key)

    s.commit()
    s.close()


def create_test_data():
    """ Creates test data. 
    Uses release_dao and task_dao's methods, 
    plus hardcoded parameters, to do so. 
    Assumes that the tables have been created and can be 
    connected to via Session. """
    s = Session()

    # Add dummy release entries for testing purposes
    # print("creating rows in the releases table...")
    release_dao.manual_create_release(3, "2021.09", "PENDING")
    release_dao.manual_create_release(4, "2021.07", "SUCCESS")

    task_dao.manual_create_task(1, "Create Release in JIRA", "SUCCESS", 4, 1)
    task_dao.manual_create_task(2, "Cut integration branch", "SUCCESS", 4, 2)
    task_dao.manual_create_task(
        3, "Update CI env with the latest integration branch", "SUCCESS", 4, 3
    )
    task_dao.manual_create_task(4, "Generate release notes", "SUCCESS", 4, 4)
    task_dao.manual_create_task(5, "Run Load Tests", "SUCCESS", 4, 5)
    task_dao.manual_create_task(
        6, "Merge integration branch into stable and tag release", "SUCCESS", 4, 6
    )
    task_dao.manual_create_task(
        7, "Mark gen3 release as released in JIRA", "SUCCESS", 4, 7
    )

    task_dao.manual_create_task(8, "Create Release in JIRA", "SUCCESS", 3, 1)
    task_dao.manual_create_task(9, "Cut integration branch", "SUCCESS", 3, 2)
    task_dao.manual_create_task(
        10, "Update CI env with the latest integration branch", "PENDING", 3, 3
    )


def reseed():
    """ Combines clear_tables() and create_test_data
    to reset the DB to a known state. """

    clear_tables()
    create_test_data()


if __name__ == "__main__":
    reseed()
