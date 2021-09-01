import os
import sqlalchemy as sa

# from config import DATABASE_URL
from . import config
from .models import Release

from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

import logging

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


def manual_create_release(key, version, result):
    """ Given int key, string version, and string result, 
    creates a Release object, and inserts it into the database controlled
    by the currently active session. 
    Assumes that the key given is unique. """

    with session_scope() as session:
        try:
            if key in get_rel_keys():
                raise Exception(
                    "That keyvalue (" + str(key) + ") is already in the database. "
                )
            current_release = Release(release_id=key, version=version, result=result)
        except Exception as e:
            print(e)
            return None
        log.info(f"Adding entry {key} to the releases table...")
        session.add(current_release)


def create_release(version, result):
    """ Given string version, and string result, creates a Release object, 
    and inserts it into the database provided by session_scope. 
    Autonatically generates a release_id that will work based on the keys already in the table. 
    Uses the minimum unused integer (min 0). 
    Depends on getkeys. """

    with session_scope() as session:
        curr_keys = get_rel_keys()
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

        current_release = Release(release_id=min_key, version=version, result=result)

        session.add(current_release)


def read_release(key):
    """ Given the (int) key of the Release to be read, returns a Release Object in the format:
    'Key: %key, Name: %name, Version: %version, Result: %result', where 
    each %value is the value corresponding to the given key. 
    Assumes that the given key is present in the database. """

    with session_scope() as session:

        try:
            release = session.query(Release).get(key)
            assert release != None
        except Exception as e:
            log.info(
                f"Attempted to retrieve key {key} from Releases, but could not locate. "
            )

        # Note: check how many errors this throws if release breaks.
        log.info(f"Retrieved release {release} from the database.")
        session.expunge_all()
        return release


def update_release(key, property, new_value):
    """ Given the key of a release, the name of the property to be changed, 
    and the intended new value of the property, change the value in the 
    database to reflect the intended change. 
    We assume that an entry with the key exists in the DB, that the property is a legit 
    property name, and that the newValue is appropriate (same type). """

    with session_scope() as session:
        release = session.query(Release).get(key)
        setattr(release, property, new_value)
        log.info(f"Changed parameter {property} of entry {key} to {new_value}. ")


def del_release(key):
    """ Given the key of a particular Release, delete it from the table. 
    If the key is not in the database, prints an error message. 
    SUPERSEDED BY deleterelease, which should be more general. """

    with session_scope() as session:
        try:
            if type(key) != int:
                raise Exception(key)
        except Exception as e:
            print(str(e) + " is not an int. Check your types. ")
            return

        try:
            session.delete(session.query(Release).get(key))
        except Exception as e:
            print("Cannot delete: " + str(key) + " is not in the database")
            log.info(f"Entry {key} was deleted from Releases table. ")


def delete_release(input):
    """ Given the key of a particular Release, delete it from the table. 
    If input is an integer, use that as the key. 
    If input is a list of integers, delete each object with one of the 
    given keys in the list. 
    If an input within the list is not in the database, or is not an 
    integer, deleteRelease will delete the others as expected, 
    throwing an exception message only for the absent key. 
    Relies on del_release for each operation.  """

    with session_scope() as session:
        if type(input) is int:
            del_release(input)
        elif type(input) is list:
            for i in input:
                del_release(i)
            log.info(f"All entries in list {input} were deleted. ")


def get_rel_num():
    """ Gets the number of entries in the current database table. 
    Returns this number as an integer. """

    with session_scope() as session:
        rows = session.query(Release).count()
        return rows


def get_rel_keys():
    """ Gets all primary keys from the current database table (Releases). 
    All keys are currently ints, so will return all ints. """

    key_list = []

    with session_scope() as session:
        for release in session.query(Release):
            key_list.append(release.release_id)
        return key_list
