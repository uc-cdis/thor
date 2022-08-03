### models.py ###

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Identity
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint

Base = declarative_base()

db = SQLAlchemy()

class Release(Base):
    __tablename__ = "releases"
    __table_args__ = db.UniqueConstraint("version")

    release_id = Column(
        Integer, primary_key=True, autoincrement=True, nullable=False
    )  # Unique arbitrary int assigned when input

    version = Column(String)  # expected to be in form 20XX.YY
    # Also now expected to be unique from release to release.
    # In the future, if we move past monthly release cycles,
    # we will need to implement names like "20XX.YYa", "20XX.YYb", etc.

    result = Column(String)  # expected to be "success", "failed", or "in progress"

    UniqueConstraint("version")

    def __repr__(self):
        return "release_ID: '{}', Version: '{}', Result: '{}'".format(
            self.release_id, self.version, self.result
        )


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(
        Integer, primary_key=True
    )  # Unique arbitrary int assigned at input
    task_name = Column(String)  # Name of task (e.g. "cut_integration_branch")
    status = Column(String)  # expected to be "success", "failed", or "in progress"
    release_id = Column(Integer, ForeignKey("releases.release_id"), nullable=False)
    step_num = Column(Integer)

    UniqueConstraint("step_num", "release_id")
    # This should enforce uniqueness when trying to write a
    # step_num and release_id pair that are already in the DB.

    def __repr__(self):
        return "ID: '{}', Name: '{}', Status: '{}', Release ID: '{}', Task Num: '{}'".format(
            self.task_id, self.task_name, self.status, self.release_id, self.step_num
        )
