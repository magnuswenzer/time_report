import datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

from time_report import utils
from time_report.models import engine, Project, TimeLog, DateInfo, TimeSubmit


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def add_object(obj: SQLModel) -> None:
    with Session(engine) as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)


def add_objects(*args: SQLModel) -> None:
    for arg in args:
        print(f'{arg=}')
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


def get_project_time_logs(proj: Project, date_stop: datetime.date):
    start = datetime.datetime(datetime.datetime.now().year, 1, 1)
    _, end = utils.get_day_range(date_stop)
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.project_id == proj.id,
                                          TimeLog.time_start >= start,
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


def get_date_info(date: datetime.date = None) -> DateInfo:
    with Session(engine) as session:
        statement = select(DateInfo).where(DateInfo.date == date)
        results = session.exec(statement)
        return results.first()


def get_dates_info(date_start: datetime.date = None, date_stop: datetime.date = None) -> list[DateInfo]:
    with Session(engine) as session:
        statement = select(DateInfo)
        print(f'{date_start=}')
        if date_start:
            statement = statement.where(DateInfo.date >= date_start)
        if date_stop:
            statement = statement.where(DateInfo.date <= date_stop)
        return list(session.exec(statement.order_by(DateInfo.date)))


def get_time_submits(date_start: datetime.date = None,
                     date_stop: datetime.date = None,
                     proj: Project = None) -> list[TimeSubmit]:
    with Session(engine) as session:
        statement = select(TimeSubmit)
        if proj:
            statement = statement.where(Project.id == proj.id)
        if date_start:
            statement = statement.where(TimeSubmit.date >= date_start)
        if date_stop:
            statement = statement.where(TimeSubmit.date <= date_stop)
        return list(session.exec(statement.order_by(TimeSubmit.date)))


