import datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

from time_report import utils
from time_report.models import engine, Project, TimeLog


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def add_object(obj: SQLModel) -> None:
    with Session(engine) as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)


def add_objects(*args: SQLModel) -> None:
    with Session(engine) as session:
        session.add_all(args)
        session.commit()


def get_project(name: str | int):
    with Session(engine) as session:
        if type(name) == str:
            statement = select(Project).where(Project.name == name)
        else:
            statement = select(Project).where(Project.id == name)
        results = session.exec(statement)
        proj = results.first()
        if not proj:
            return
        return proj


def get_projects() -> list[Project]:
    with Session(engine) as session:
        statement = select(Project)
        return list(session.exec(statement))


def get_time_logs_for_project(proj: Project) -> list[TimeLog]:
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.project_id == proj.id)
        return list(session.exec(statement))


def get_time_logs_for_day(dtime: datetime.datetime):
    start, end = utils.get_day_range(dtime)
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.time_start >= start,
                                          TimeLog.time_start <= end)
        return list(session.exec(statement))


def get_project_time_logs_for_day(proj: Project, dtime: datetime.datetime):
    start, end = utils.get_day_range(dtime)
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.project_id == proj.id,
                                          TimeLog.time_start >= start,
                                          TimeLog.time_start <= end)
        return list(session.exec(statement))


def get_project_time_logs_for_week(proj: Project, week_number: int | str):
    start, end = utils.get_week_range(week_number)
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.project_id == proj.id,
                                          TimeLog.time_start >= start,
                                          TimeLog.time_start <= end)
        return list(session.exec(statement))


def get_running_time_log() -> TimeLog | None:
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.time_stop == None)
        results = session.exec(statement)
        tlog = results.first()
        if not tlog:
            return
        return tlog

