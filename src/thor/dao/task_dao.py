import sqlalchemy as sa
import os
import logging

from thor.dao import config
from thor.dao.models import Task
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
def manual_create_task(key, name, status, release_id, step_num):
    """ Given int ID, string name, string status, int release_id, and int step_num,
    creates a Task object, and inserts it into the database controlled
    by the currently active session (tasks DB). 
    Note that release_id is a foreign key corresponding to Release DB. 
    Throws exceptions if the key is already in the database. """

    with session_scope() as session:
        try:
            if key in get_task_keys():
                raise Exception(
                    f"That keyvalue {str(key)} is already in the database. "
                )
            current_task = Task(
                task_id=key, task_name=name, status=status, release_id=release_id, step_num=step_num
            )
        except Exception as e:
            print(e)
            return None
        else:
            log.info(f"Manually adding entry {key} to Tasks table.")
            session.add(current_task)


def create_task(name, status, release_id, step_num):
    """ Given string name (version name), string status, int release_id, and int step_num
    creates a Task object, and inserts it into the database controlled
    by the currently active session (TaskDB). Returns the new task ID. 
    Autonatically generates an ID that will work based on the IDs already in the table. 
    Uses the minimum unused integer (min 0). 
    Depends on getkeys. 
    NOTE: release_id is expected to correspond with an existing release
    in the database. If not, probably nothing should break, but we may 
    see some unexpected behavior. Best to avoid if possible. """

    with session_scope() as session:
        curr_keys = get_task_keys()
        curr_keys.sort()

        # The following code generates the minimum working ID in the database.
        minimal_task_ids = set(range(len(curr_keys)))
        unused_ids = minimal_task_ids - set(curr_keys)
        if unused_ids:
            min_key = list(unused_ids)[0]
        else:
            min_key = curr_keys[-1] + 1

        currentTask = Task(
            task_id=min_key, task_name=name, status=status, release_id=release_id, step_num=step_num
        )
        log.info(f"Added task {min_key} to Tasks table")

        session.add(currentTask)
        return min_key


def read_task(key):
    """ Given the (int) key of the Task to be read, returns a Task Object in the format:
    'Key: %key, Name: %name, Version: %version, Status: %status, Task Num: %step_num', where 
    each %value is the value corresponding to the given key. 
    Throws an Exception if the key value is not in the database.  """

    with session_scope() as session:

        try:
            task = session.query(Task).get(key)
            assert task != None
        except Exception as e:
            log.info(
                f"Attempted to retrieve key {key} from Tasks, but could not locate. "
            )
        else:
            # Note: check how many errors this throws if release breaks.
            log.info(f"Retrieved task {task} from the database.")
            session.expunge_all()
            return task


def read_all_tasks():
    """ Returns a list of all Task objects in the Tasks table of te database. 
    Primarily to be used by main:app/tasks, as it must call get_all_tasks
    in a somewhat inefficient manner otherwise. """

    with session_scope() as session:

        # There's something seriously screwed up here.
        # Returning the list directly causes the test to fail,
        # and the encoder outputs empty dicts instead of proper
        # formatted objects. But if we go through a "temp" variable,
        # everything works for some reason.
        #
        # The expunge is also necessary, but I *don't know how it works.*
        # It has to be in this location, or the same error occurs.

        temp = [task for task in session.query(Task)]
        session.expunge_all()
        return temp


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
            log.info(f"Entry {key} was deleted from Tasks table. ")
        except Exception as e:
            print(f"Cannot delete: {str(key)} is not in the database")
            log.info(f"Failed to find entry with key {key} to delete. ")


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


def get_num_tasks():
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


def lookup_task_key(desired_task_name, desired_release_id):
    """ Given string task_name and int release_id, 
    searches the Tasks database for matching Tasks, 
    and returns an int corresponding to the matching Task. 
    If there is no corresponding Task, returns None. 
    
    NOTE: The combination of task_name and release_id 
    should be unique for each Task. TODO: Make this throw
    loud errors if it discovers more than one Task
    with corresponding task_name and release_id. """

    with session_scope() as session:
        key_list = get_task_keys()

        for key in key_list:
            current_task = read_task(key)
            if (
                current_task.task_name == desired_task_name
                and current_task.release_id == desired_release_id
            ):

                return key
        return None


if __name__ == "__main__":
    print(read_all_tasks())

    wanted_string = "Update CI env with the latest integration branch"
    wanted_id = 3

    # print(lookup_key(wanted_string, wanted_id))
