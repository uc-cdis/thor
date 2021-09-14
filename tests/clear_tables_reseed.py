# clear_tables_reseed.py

import sqlalchemy as sa
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker
from thor.dao import config
from thor.dao.models import Release, Task
from thor.create_all_tables import meta

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


if __name__ == "__main__":
    clear_tables()
