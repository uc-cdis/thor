import os
import sqlalchemy as sa
from sqlalchemy.sql.sqltypes import String

from thor.dao import config
from thor.dao.models import Release

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


def manual_create_release(release_id, version, result):
    """ Given int release_id, string version, and string result, 
    creates a Release object, and inserts it into the database controlled
    by the currently active session. 
    Assumes that the release_id given is unique. 

    Throws errors if any input type is not as expected, 
    or if the given release_id is already present in the database. """

    with session_scope() as session:
        try:
            if not isinstance(release_id, int):
                raise TypeError(
                    f"The value for release_id, {release_id} is not an int."
                )
            if not isinstance(version, str):
                raise TypeError(f"The value for version, {version} is not a string.")
            if not isinstance(result, str):
                raise TypeError(f"The value for result, {result} is not a string.")

            if release_id in get_release_keys():
                raise ValueError(
                    f"ERROR: That keyvalue {str(release_id)} is already in the database. "
                )
            current_release = Release(
                release_id=release_id, version=version, result=result
            )

        except ValueError as value_error:
            print(value_error)
        except TypeError as type_error:  # this is also raised if we don't have enough parameters input
            print(type_error)
        except Exception as e:
            print(e)

        log.info(f"Adding entry {release_id} to the releases table...")
        session.add(current_release)


def create_release(version, result):
    """ Given string version, and string result, creates a Release object, 
    and inserts it into the database provided by session_scope. 
    Autonatically generates a release_id that will work based on the keys already in the table. 
    Uses the minimum unused integer (min 0). 
    Depends on get_release_keys. 
    Throws errors if the given 'version' or 'result' are not Strings. """

    curr_keys = get_release_keys()

    with session_scope() as session:
        curr_keys.sort()

        try:
            if not isinstance(version, str):
                raise TypeError(f"The value for version, {version} is not a string.")
            if not isinstance(result, str):
                raise TypeError(f"The value for result, {result} is not a string.")
        except TypeError as type_error:
            print(type_error)

        # Thanks to Brian for working out this set difference method.
        # By generating 2 sets, one with the existing keys,
        # and one with optimally allocated keys, we can use their difference
        # to figure out the minimum keys that haven't been used.

        minimal_release_ids = set(range(len(curr_keys)))
        unused_ids = minimal_release_ids - set(curr_keys)
        if unused_ids:
            min_key = list(unused_ids)[0]
        else:
            min_key = curr_keys[-1] + 1

        current_release = Release(release_id=min_key, version=version, result=result)

        session.add(current_release)


def read_release(release_id):
    """ Given the (int) release_id of the Release to be read, returns a Release Object in the format:
    'release_id: %release_id, Name: %name, Version: %version, Result: %result', where 
    each %value is the value corresponding to the given release_id. 
    Assumes that the given release_id is present in the database. 
    Throws errors if the given release_id is not an int, or if it is not in the database. """

    with session_scope() as session:

        try:
            if not isinstance(release_id, int):
                print(release_id, type(release_id))
                raise TypeError(
                    f"The value given for release_id, {release_id} is not an int."
                )

            release = session.query(Release).get(release_id)

            assert release != None

        except TypeError as type_error:
            print(type_error)
            log.info("Could not retrieve: " + str(type_error))

        except Exception:
            log.info(
                f"Attempted to retrieve release_id {release_id} from Releases, but could not locate. "
            )

        # Note: check how many errors this throws if release breaks.
        log.info(f"Retrieved release {release} from the database.")
        session.expunge_all()
        return release


def read_all_releases():
    """ Returns a list of all Release objects in the Releases table of te database. 
    Primarily to be used by main:app/releases, as it must call get_all_releases
    in a somewhat inefficient manner otherwise. """

    print("\n\n read_all_releases start \n\n")

    with session_scope() as session:

        # There's something seriously screwed up here.
        # Returning the list directly causes the test to fail,
        # and the encoder outputs empty dicts instead of proper
        # formatted objects. But if we go through a "temp" variable,
        # everything works for some reason.
        #
        # The expunge is also necessary, but I *don't know how it works.*
        # It has to be in this location, or the same error occurs.

        temp = [release for release in session.query(Release)]
        session.expunge_all()
        return temp


def update_release(release_id, property, new_value):
    """ Given the release_id of a release, the name of the property to be changed, 
    and the intended new value of the property, change the value in the 
    database to reflect the intended change. 
    We assume that an entry with the release_id exists in the DB, that the property is a legit 
    property name, and that the newValue is appropriate (same type). """

    with session_scope() as session:
        release = session.query(Release).get(release_id)
        setattr(release, property, new_value)
        log.info(f"Changed parameter {property} of entry {release_id} to {new_value}. ")


def delete_release(release_id):
    """ Given the release_id of a particular Release, delete it from the table. 
    If the release_id is not in the database, prints an error message. 
    Used by delete_releases. """

    with session_scope() as session:
        # Did not use type() below, to guard against possible subclasses of int
        if not isinstance(release_id, int):
            print(str(release_id) + " is not an int. Check your types. ")
            return

        try:
            session.delete(session.query(Release).get(release_id))
        except Exception:
            print(f"Cannot delete: {release_id} is not in the database")
            log.info(f"Entry {release_id} was deleted from Releases table. ")


def delete_releases(input):
    """ Given a list of release_ids (ints), delete each object with one of the 
    given release_ids in the list. 

    If the input is not a list, throws a TypeError. 
    If an input within the list is not in the database, or is not an 
    integer, deleteReleases will delete the others as expected, 
    throwing an exception message only for the absent release_id. 

    Relies on delete_release for each operation.  """

    with session_scope() as session:
        if not isinstance(input, list):
            raise TypeError(input)
        else:
            for i in input:
                delete_release(i)
            log.info(f"All entries in list {input} were deleted. ")


def get_release_num():
    """ Gets the number of entries in the current database table. 
    Returns this number as an integer. """

    with session_scope() as session:
        rows = session.query(Release).count()
        return rows


def get_release_keys():
    """ Gets all primary keys (release_id) from the current database table (Releases). 
    All keys are currently ints, so will return a list of ints. """

    with session_scope() as session:
        return [release.release_id for release in session.query(Release)]


class look_upper:
    def __init__(self):
        True

    def release_id_lookup(self, given_version):
        """ Given a string version of a specific release, 
        return as int the corresponding release_id of the release. 
        Currently behaves badly if 'version' does not correspond exactly
        to a version string already in the database. 
        Should fix to be more resilient. 
        Also assumes that 'version' is unique to each Release object. 
            This is a design decision that may cause problems in the 
            future, but having a 1-to-1 mapping from 'version' to id
            will be quite valuable for creating Tasks linked to Releases. """

        with session_scope() as session:
            for release in session.query(Release):
                if release.version == given_version:
                    return release.release_id


if __name__ == "__main__":
    print(read_all_releases())
