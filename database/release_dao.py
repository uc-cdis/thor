import sqlalchemy as sa
from config import DATABASE_URL
from models import Release
from sqlalchemy.orm import sessionmaker

# Needs to implement all CRUD operations on the given database.

engine = sa.create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

s = Session()


def manCreateRelease(id, name, version, result):
    """ Given int ID, string name, string version, and string result, 
    creates a Release object, and inserts it into the database controlled
    by the currently active session. 
    Assumes that the id given is unique. """

    try:
        if id in getkeys():
            raise Exception(
                "That keyvalue (" + str(id) + ") is already in the database. "
            )
        currentRelease = Release(id=id, name=name, version=version, result=result)
    except Exception as e:
        print(e)
    else:
        s.add(currentRelease)


def createRelease(name, version, result):
    """ Given string name, string version, and string result, 
    creates a Release object, and inserts it into the database controlled
    by the currently active session. 
    Autonatically generates an ID that will work based on the IDs already in the table. 
    Uses the minimum unused integer (min 0). 
    Depends on getkeys. """

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

    currentRelease = Release(id=minID, name=name, version=version, result=result)

    s.add(currentRelease)


def readRelease(id):
    """ Given the (int) ID of the Release to be read, returns a string in the format:
    'ID: %ID, Name: %name, Version: %version, Result: %result', where 
    each %value is the value corresponding to the given ID. 
    Assumes that the given ID is present in the database. """

    outstring = "The ID (" + str(id) + ") is not in the database. "

    try:
        rel = s.query(Release).get(id)
        assert rel != None
    except Exception as e:
        pass
    else:
        outstring = "ID: '{}', Name: '{}', Version: '{}', Result: '{}'".format(
            rel.id, rel.name, rel.version, rel.result
        )

    return outstring


def updateRelease(id, property, newValue):
    """ Given the id of a release, the name of the property to be changed, 
    and the intended new value of the property, change the value in the 
    database to reflect the intended change. 
    We assume that the id exists in the DB, that the property is a legit 
    property name, and that the newValue is appropriate (int vs str). """

    rel = s.query(Release).get(id)
    setattr(rel, property, newValue)


def delRelease(id):
    """ Given the id of a particular Release, delete it from the table. 
    If the id is not in the database, prints an error message. 
    SUPERSEDED BY deleterelease, which should be more general. """

    try:
        if type(id) != int:
            raise Exception(id)
    except Exception as e:
        print(str(e) + " is not an int. Check your types. ")
        return

    try:
        s.delete(s.query(Release).get(id))
    except Exception as e:
        print("Cannot delete: " + str(id) + " is not in the database")


def deleteRelease(input):
    """ Given the id of a particular Release, delete it from the table. 
    If input is an integer, use that as the key (id). 
    If input is a list of integers, delete each object with one of the 
    given keys in the list. 
    If an input within the list is not in the database, or is not an 
    integer, deleteRelease will delete the others as expected, 
    throwing an exception message only for the absent key. 
    Relies on delRelease for each operation.  """

    if type(input) is int:
        delRelease(input)
    elif type(input) is list:
        for i in input:
            delRelease(i)


def getnum():
    """ Gets the number of entries in the current database table. 
    Returns this number as an integer. """
    rows = s.query(Release).count()
    return rows


def getkeys():
    """ Gets all primary keys from the current database table (Releases). 
    All keys are currently ints, so will return all ints. """
    keylist = []
    for rel in s.query(Release):
        keylist.append(rel.id)
    return keylist

s.commit()

s.close()
