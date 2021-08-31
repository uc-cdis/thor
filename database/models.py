### models.py ###

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()


class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True)  # Unique arbitrary int assigned when input
    version = Column(String)  # expected to be in form 20XX.YY
    result = Column(String)  # expected to be "success", "failed", or "in progress"

    def __repr__(self):
        return "ID: '{}', Version: '{}', Result: '{}'".format(
            self.id, self.version, self.result
        )


class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(
        Integer, primary_key=True
    )  # Unique arbitrary int assigned at input
    task_name = Column(String)  # Name of task (e.g. "cut_integration_branch")
    status = Column(String)  # expected to be "success", "failed", or "in progress"
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)

    def get_release_id(self):
        return self.release_id

    def __repr__(self):
        return "ID: '{}', Name: '{}', Status: '{}', Release ID: '{}'".format(
            self.task_id, self.task_name, self.status, self.release_id
        )
