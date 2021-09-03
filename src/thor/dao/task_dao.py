import sqlalchemy as sa
import os
import logging

from dao import config
from dao.models import Task
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Implements CRUD functions on the database.

engine = sa.create_engine(config.DATABASE_URL)
Session = sessionmaker(bind=engine)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
log = logging.getLogger(__name__)


@contextmanager
def session_scope():
    """ Provides transactional scope around a series of operations. 
    In other words, handles the messiness of sessions and commits, 
    including rollback, so other modules don't have to. """

    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


# TODO: Investigate possibility of merging this functionality with release_dao.
def manual_create_task(key, name, status, release_id):
    """ Given int ID, string name, string status, and int release_id, 
    creates a Task object, and inserts it into the database controlled
    by the currently active session (tasks DB). 
    Note that release_id is a foreign key corresponding to Release DB. 
    Throws exceptions if the key is already in the database. """

    with session_scope() as session:
        try:
            if key in get_task_keys():
                raise Exception(
                    "That keyvalue (" + str(key) + ") is already in the database. "
                )
            current_task = Task(
                task_id=key, task_name=name, status=status, release_id=release_id
            )
        except Exception as e:
            print(e)
            return None
        log.info(f"Manually adding entry {key} to Tasks table.")
        session.add(current_task)


def create_task(name, status, release_id):
    """ Given string version, and string result, 
    creates a Task object, and inserts it into the database controlled
    by the currently active session (TaskDB). 
    Autonatically generates an ID that will work based on the IDs already in the table. 
    Uses the minimum unused integer (min 0). 
    Depends on getkeys. """

    with session_scope() as session:
        curr_keys = get_task_keys()
        curr_keys.sort()
        min_key = curr_keys[0]
        for key in curr_keys[1:]:
            if key != min_key + 1:
                min_key += 1
                break
            else:
                min_key += 1
        if min_key == curr_keys[-1]:
            min_key += 1

        currentTask = Task(
            task_id=min_key, task_name=name, status=status, release_id=release_id
        )
        log.info(f"Added task {min_key} to Tasks table")

        session.add(currentTask)


def read_task(key):
    """ Given the (int) key of the Task to be read, returns a Task Object in the format:
    'Key: %key, Name: %name, Version: %version, Result: %result', where 
    each %value is the value corresponding to the given key. 
    Assumes that the given key is present in the database. """

    with session_scope() as session:

        try:
            task = session.query(Task).get(key)
            assert task != None
        except Exception as e:
            log.info(
                f"Attempted to retrieve key {key} from Tasks, but could not locate. "
            )

        # Note: check how many errors this throws if release breaks.
        log.info(f"Retrieved task {task} from the database.")
        session.expunge_all()
        return task


def update_task(key, property, new_value):
    """ Given the key of a Task, the name of the property to be changed, 
    and the intended new value of the property, change the value in the 
    database to reflect the intended change. 
    We assume that the id exists in the DB, that the property is a legit 
    property name, and that the newValue is appropriate (type checking). """

    with session_scope() as session:
        release = session.query(Task).get(key)
        setattr(release, property, new_value)
        log.info(f"Changed parameter {property} of {key} to {new_value}. ")


def del_task(key):
    """ Given the id of a particular Task, delete it from the table. 
    If the id is not in the database, prints an error message. 
    SUPERSEDED BY deleterelease, which should be more general. """

    with session_scope() as session:
        try:
            if type(key) != int:
                raise Exception(key)
        except Exception as e:
            print(str(key) + " is not an int. Check your types. ")
            log.info(f"TypeError: Bad key {key} was given. Could not delete.")
            return

        try:
            session.delete(session.query(Task).get(key))
        except Exception as e:
            print("Cannot delete: " + str(key) + " is not in the database")
            log.info(f"Failed to find entry with key {key} to delete. ")
        log.info(f"Entry {key} was deleted from Tasks table. ")


def delete_task(input):
    """ Given the key of a particular Task, delete it from the table. 
    If input is an integer, use that as the key . 
    If input is a list of integers, delete each object with one of the 
    given keys in the list. 
    If an input within the list is not in the database, or is not an 
    integer, deleteTask will delete the others as expected, 
    throwing an exception message only for the absent key. 
    Relies on del_task for each operation.  """

    if type(input) is int:
        del_task(input)
    elif type(input) is list:
        for i in input:
            del_task(i)
        log.info(f"All entries in list {input} were deleted. ")


def get_task_num():
    """ Gets the number of entries in the current database table. 
    Returns this number as an integer. """

    with session_scope() as session:

        rows = session.query(Task).count()
        return rows


def get_task_keys():
    """ Gets all primary keys from the current database table (Task DB). 
    All keys are currently ints, so will return all ints. """
    key_list = []

    with session_scope() as session:

        for release in session.query(Task):
            key_list.append(release.task_id)
        return key_list
