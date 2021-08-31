import os
import sqlalchemy as sa
from dao.config import RELEASE_DATABASE_URL
from dao.models import Release

from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

import logging

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


def manCreateRelease(id, version, result):
    """ Given int ID, string version, and string result, 
    creates a Release object, and inserts it into the database controlled
    by the currently active session. 
    Assumes that the id given is unique. """

    with session_scope() as session:
      try:
        if id in getRKeys():
            raise Exception(
                "That keyvalue (" + str(id) + ") is already in the database. "
            )
        currentRelease = Release(id=id, version=version, result=result)
      except Exception as e:
        print(e)
        return None
      l.info("Adding entry to the releases table...")
      session.add(currentRelease)


def createRelease(version, result):
    with session_scope() as s:
        try:
            if id in getRKeys():
                raise Exception(
                    "That keyvalue (" + str(id) + ") is already in the database. "
                )
            currentRelease = Release(id=id, version=version, result=result)
        except Exception as e:
            print(e)
            return None
        l.info(f"Manually adding entry {id} to Releases table.")
        s.add(currentRelease)


def createRelease(version, result):
    with session_scope() as session:
      currIDs = getkeys()
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

      currentRelease = Release(id=minID, version=version, result=result)

      session.add(currentRelease)


def readRelease(id):
    with session_scope() as session:
      outstring = "The ID (" + str(id) + ") is not in the database. "

      try:
        rel = session.query(Release).get(id)
        assert rel != None
      except Exception as e:
        pass
      
      #outstring = "ID: '{}', Version: '{}', Result: '{}'".format(
      #      rel.id, rel.version, rel.result
      #  )

      # log.info("### ##" + str(type(rel)))
      log.info(f"retrieved release {rel} from the database...")
      session.expunge_all()
      return rel


def readRelease(id):
    with session_scope() as s:
        # outstring = "The ID (" + str(id) + ") is not in the database. "

        try:
            rel = s.query(Release).get(id)
            # print(rel, rel == None)
            assert rel != None
        except Exception as e:
            pass
            # print("The ID " + str(id) + " is not in the database. ")
        # else:
        #     outstring = "ID: '{}', Name: '{}', Version: '{}', Result: '{}'".format(
        #         rel.id, rel.name, rel.version, rel.result
        #     )

        l.info(f"Retrieved release{rel} from the database. ")
        s.expunge_all()
        return rel


def updateRelease(id, property, newValue):
    with session_scope() as session:
      rel = session.query(Release).get(id)
      setattr(rel, property, newValue)
      l.info(f"Changed parameter {property} of {id} to {newValue}. ")


def delRelease(id):
    with session_scope() as session:
      try:
        if type(id) != int:
            raise Exception(id)
      except Exception as e:
        print(str(e) + " is not an int. Check your types. ")
        return

      try:
        session.delete(s.query(Release).get(id))
      except Exception as e:
        print("Cannot delete: " + str(id) + " is not in the database")
        l.info(f"Entry {id} was deleted from Releases table. ")


def deleteRelease(input):
    with session_scope() as session:
      if type(input) is int:
        delRelease(input)
      elif type(input) is list:
        for i in input:
            delRelease(i)
        l.info(f"All entries in list {input} were deleted. ")


def getRNum():
    with session_scope() as session:
      rows = session.query(Release).count()
      return rows

def getRKeys():
    keylist = []
    
    with session_scope() as session:
        for rel in session.query(Release):
            keylist.append(rel.id)
        return keylist
