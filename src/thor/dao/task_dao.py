import sqlalchemy as sa
import os
import logging

from dao.config import RELEASE_DATABASE_URL
from dao.models import Task
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# Implements CRUD functions on the database.

engine = sa.create_engine(RELEASE_DATABASE_URL)
Session = sessionmaker(bind=engine)

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
l = logging.getLogger(__name__)


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


def manCreateTask(id, name, status, release_id):
    """ Given int ID, string name, string status, and int release_id, 
    creates a Task object, and inserts it into the database controlled
    by the currently active session (Task DB). 
    Note that release_id is a foreign key corresponding to Release DB. 
    Assumes that the id given is unique. """

    with session_scope() as s:
        try:
            if id in getTKeys():
                raise Exception(
                    "That keyvalue (" + str(id) + ") is already in the database. "
                )
            currentTask = Task(
                task_id=id, task_name=name, status=status, release_id=release_id
            )
        except Exception as e:
            print(e)
            return None
        l.info(f"Manually adding entry {id} to Tasks table.")
        s.add(currentTask)


def createTask(name, status, release_id):
    """ Given string version, and string result, 
    creates a Task object, and inserts it into the database controlled
    by the currently active session (TaskDB). 
    Autonatically generates an ID that will work based on the IDs already in the table. 
    Uses the minimum unused integer (min 0). 
    Depends on getkeys. """

    with session_scope() as s:
        currIDs = getTKeys()
        currIDs.sort()
        minID = currIDs[0]
        for id in currIDs[1:]:
            if id != minID + 1:
                minID += 1
                break
            else:
                minID += 1
        if minID == currIDs[-1]:
            minID += 1

        currentTask = Task(
            task_id=minID, task_name=name, status=status, release_id=release_id
        )
        l.info(f"Added task {minID} to Tasks table")

        s.add(currentTask)


def readTask(id):
    """ Given the (int) ID of the Task to be read, returns a Task object in the format:
    'ID: %ID, Name: %name, Version: %version, Result: %result', where 
    each %value is the value corresponding to the given ID. 
    Assumes that the given ID is present in the database. """

    with session_scope() as s:
        # outstring = "The ID (" + str(id) + ") is not in the database. "

        try:
            task = s.query(Task).get(id)
            # print(rel, rel == None)
            assert task != None
        except Exception as e:
            pass
            # print("The ID " + str(id) + " is not in the database. ")
        # else:
        #     outstring = "ID: '{}', Name: '{}', Version: '{}', Result: '{}'".format(
        #         rel.id, rel.name, rel.version, rel.result
        #     )

        l.info(f"Retrieved task {task} from the database. ")
        s.expunge_all()
        return task


def updateTask(id, property, newValue):
    """ Given the id of a Task, the name of the property to be changed, 
    and the intended new value of the property, change the value in the 
    database to reflect the intended change. 
    We assume that the id exists in the DB, that the property is a legit 
    property name, and that the newValue is appropriate (type checking). """

    with session_scope() as s:
        rel = s.query(Task).get(id)
        setattr(rel, property, newValue)
        l.info(f"Changed parameter {property} of {id} to {newValue}. ")


def delTask(id):
    """ Given the id of a particular Task, delete it from the table. 
    If the id is not in the database, prints an error message. 
    SUPERSEDED BY deleterelease, which should be more general. """

    with session_scope() as s:
        try:
            if type(id) != int:
                raise Exception(id)
        except Exception as e:
            print(str(e) + " is not an int. Check your types. ")
            return

        try:
            s.delete(s.query(Task).get(id))
        except Exception as e:
            print("Cannot delete: " + str(id) + " is not in the database")
        l.info(f"Entry {id} was deleted from Tasks table. ")


def deleteTask(input):
    """ Given the id of a particular Task, delete it from the table. 
    If input is an integer, use that as the key (id). 
    If input is a list of integers, delete each object with one of the 
    given keys in the list. 
    If an input within the list is not in the database, or is not an 
    integer, deleteTask will delete the others as expected, 
    throwing an exception message only for the absent key. 
    Relies on delTask for each operation.  """

    with session_scope() as s:

        if type(input) is int:
            delTask(input)
        elif type(input) is list:
            for i in input:
                delTask(i)
            l.info(f"All entries in list {input} were deleted. ")


def getTNum():
    """ Gets the number of entries in the current database table. 
    Returns this number as an integer. """

    with session_scope() as s:

        rows = s.query(Task).count()
        return rows


def getTKeys():
    """ Gets all primary keys from the current database table (Task DB). 
    All keys are currently ints, so will return all ints. """
    keylist = []

    with session_scope() as s:

        for rel in s.query(Task):
            keylist.append(rel.task_id)
        return keylist
