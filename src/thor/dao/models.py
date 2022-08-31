### models.py ###
import enum
import json

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint

Base = declarative_base()

class Release(Base):
    __tablename__ = "releases"
    __table_args__ = (UniqueConstraint("version"),)

    release_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )  # Unique arbitrary int assigned when input - autoincrement controlled

    version = Column(String, unique=True)  # expected to be in form 20XX.YY
    # Also now expected to be unique from release to release.
    # In the future, if we move past monthly release cycles,
    # we will need to implement names like "20XX.YYa", "20XX.YYb", etc.
    # Note: processing for env var exposure expects 20XX.YY

    __table_args__ = (UniqueConstraint("version"),)

    class ReleaseResults(enum.Enum):
        PENDING = "PENDING"
        RUNNING = "RUNNING"
        PAUSED  = "PAUSED"
        RELEASED = "RELEASED"

        def __str__(self):
            return self.name

    result = Column(Enum(ReleaseResults))
    # Note: When pulling a Release object, wrap as str(r.result) 
    # as this will be an enum otherwise

    UniqueConstraint("version")

    def __str__(self):
        return f'{{"release_id": {self.release_id}, "version": {self.version}, "result": {self.result}}}'
        
    def __repr__(self):
        return json.dumps({
            "release_id": self.release_id,
            "version": self.version, 
            "result": str(self.result)
        })


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(
        Integer, primary_key=True
    )  # Unique arbitrary int assigned at input
    task_name = Column(String)  # Name of task (e.g. "cut_integration_branch")
    # note: As of 08/31/22 this is filled by job_description field in thor_config

    class TaskStatus(enum.Enum):
        PENDING = "PENDING"
        RUNNING = "RUNNING"
        FAILED  = "FAILED"
        SUCCESS = "SUCCESS"

        def __str__(self):
            return self.name

    status = Column(Enum(TaskStatus))
    # Same note as above applies here wrt enums
    release_id = Column(Integer, ForeignKey("releases.release_id"), nullable=False)
    step_num = Column(Integer)

    UniqueConstraint("step_num", "release_id")
    # This should enforce uniqueness when trying to write a
    # step_num and release_id pair that are already in the DB.

    def __repr__(self):
        return "ID: '{}', Name: '{}', Status: '{}', Release ID: '{}', Task Num: '{}'".format(
            self.task_id, self.task_name, self.status, self.release_id, self.step_num
        )
