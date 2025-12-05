import datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

from time_report import utils
from time_report.models import engine, Project, TimeLog, DateInfo, TimeSubmit, WeekInfo


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def add_object(obj: SQLModel) -> None:
    with Session(engine) as session:
        session.add(obj)
        session.commit()
        session.refresh(obj)


def add_objects(*args: SQLModel) -> None:
    # for arg in args:
    #     print(f'{arg=}')
    with Session(engine) as session:
        session.add_all(args)
        session.commit()


def get_project(name: str | int, year: int):
    with Session(engine) as session:
        if type(name) == str:
            statement = select(Project).where(Project.name == name,
                                              Project.year == year)
        else:
            statement = select(Project).where(Project.id == name,
                                              Project.year == year)
        results = session.exec(statement)
        proj = results.first()
        if not proj:
            return
        return proj


def get_projects(year: int) -> list[Project]:
    with Session(engine) as session:
        statement = select(Project)
        if year:
            statement = statement.where(Project.year == year)
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


def get_project_time_logs(year: int, proj: Project, date_stop: datetime.date = None):
    start = datetime.datetime(year, 1, 1)
    end = None
    if date_stop:
        _, end = utils.get_day_range(date_stop)
    with Session(engine) as session:
        if end:
            statement = select(TimeLog).where(TimeLog.project_id == proj.id,
                                              TimeLog.time_start >= start,
                                              TimeLog.time_start <= end)
        else:
            statement = select(TimeLog).where(TimeLog.project_id == proj.id,
                                              TimeLog.time_start >= start)
        return list(session.exec(statement))


def get_time_logs(date_start: datetime.date,
                  date_stop: datetime.date,
                  include_ongoing: bool = True):
    with Session(engine) as session:
        statement = select(TimeLog)
        if date_start:
            statement = statement.where(TimeLog.time_start >= date_start)
        if date_stop:
            end_date = date_stop + datetime.timedelta(days=1) #
            # Add a day to include the whole datetime
            statement = statement.where(TimeLog.time_stop <= end_date)
        res = list(session.exec(statement.order_by(TimeLog.time_start)))
        tlogs = [log for log in res if log.time_stop.date() <= date_stop]
        if include_ongoing:
            # print()
            # print(f"{date_stop=}")
            # print(f"{datetime.datetime.now().date()=}")
            now = datetime.datetime.now()
            if not date_stop or date_stop == now.date():
                ongoing_tlog = get_running_time_log()
                # print(f"{ongoing_tlog=}")
                if ongoing_tlog:
                    tlogs.append(ongoing_tlog)
        return tlogs


def get_time_log_by_id(_id: int) -> TimeLog | None:
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.id == _id)
        return session.exec(statement).first()


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


def get_all_time_logs_for_week(week_number: int | str):
    start, end = utils.get_week_range(week_number)
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.time_start >= start,
                                          TimeLog.time_start <= end)
        return list(session.exec(statement))


def get_running_time_log() -> TimeLog | None:
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.time_stop == None)
        results = session.exec(statement)
        all_tlogs = results.all()
        if not all_tlogs:
            return
        tlog = None
        if len(all_tlogs) == 1:
            tlog = all_tlogs[0]
        else:
            raise Exception("To many ongoing time logs. something is wrong!")
            # for tl in all_tlogs:
            #     if tl.time_start.year == year:
            #         tlog = tl
            #         break
        # tlog = results.first()
        if not tlog:
            return
        tlog.dt = datetime.datetime.now() - tlog.time_start
        return tlog


def get_date_info(date: datetime.date = None) -> DateInfo:
    with Session(engine) as session:
        statement = select(DateInfo).where(DateInfo.date == date)
        results = session.exec(statement)
        return results.first()


def get_dates_info(date_start: datetime.date = None, date_stop: datetime.date = None) -> list[DateInfo]:
    with Session(engine) as session:
        statement = select(DateInfo)
        if date_start:
            statement = statement.where(DateInfo.date >= date_start)
        if date_stop:
            statement = statement.where(DateInfo.date <= date_stop)
        return list(session.exec(statement.order_by(DateInfo.date)))


def get_week_info(week_nr: int):
    with Session(engine) as session:
        statement = select(WeekInfo).where(WeekInfo.week_number == week_nr)
        results = session.exec(statement)
        return results.first()


def get_time_submit(date: datetime.date = None,
                     proj: Project = None) -> TimeSubmit:
    with Session(engine) as session:
        statement = select(TimeSubmit).join(Project).where(Project.id == proj.id, TimeSubmit.date == date)
        results = session.exec(statement)
        return results.first()


def get_time_submits(date_start: datetime.date = None,
                     date_stop: datetime.date = None,
                     proj: Project = None) -> list[TimeSubmit]:
    with Session(engine) as session:
        statement = select(TimeSubmit)
        # statement = select(TimeSubmit).join(Project)
        if proj:
            statement = statement.join(Project)
            statement = statement.where(Project.id == proj.id)
        if date_start:
            statement = statement.where(TimeSubmit.date >= date_start)
        if date_stop:
            statement = statement.where(TimeSubmit.date <= date_stop)
        return list(session.exec(statement.order_by(TimeSubmit.date)))


def get_latest_date_in_database() -> datetime.date | None:
    with Session(engine) as session:
        statement = select(TimeLog).order_by()
        tlogs = list(session.exec(statement))
        if not tlogs:
            return
        return tlogs[-1].time_start.date()


def update_red_dates(red_dates):
    with Session(engine) as session:
        statement = select(DateInfo)
        dinfo = list(session.exec(statement))
        for di in dinfo:
            di.non_working_day = 0
            if di.date.weekday() in [5, 6]:
                di.non_working_day = 1
            elif di.date in red_dates:
                di.non_working_day = 1

            if di.non_working_day:
                di.time_in_plan = None
            # if di.date == datetime.date(2025, 4, 21):
            #     print(f"{di=}")

        session.add_all(dinfo)
        session.commit()


