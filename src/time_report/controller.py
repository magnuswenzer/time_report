from time_report import database
from time_report.models import Project, TimeLog
import datetime
from time_report import utils

def start_logging(proj: Project | str) -> None:
    stop_logging()
    if type(proj) == str:
        obj = database.get_project(proj)
        if not obj:
            raise KeyError(f'Invalid project {proj}')
        proj = obj
    tlog = TimeLog(
        time_start=datetime.datetime.now(),
        project=proj
    )
    database.add_object(tlog)


def stop_logging() -> None:
    tlog = database.get_running_time_log()
    if not tlog:
        return
    tlog.time_stop = datetime.datetime.now()
    td = utils.TimeDelta(tlog.time_stop - tlog.time_start)
    tlog.dt = td.dt
    tlog.nr_hours = td.hours
    tlog.nr_minutes = td.minutes
    database.add_object(tlog)


def add_manual_time_to_project(proj: Project, time_start: datetime.datetime, nr_minutes: int | str) -> None:
    time_stop = time_start + datetime.timedelta(minutes=int(nr_minutes))
    td = utils.TimeDelta(time_stop - time_start)
    tlog = TimeLog(
        time_start=time_start,
        time_stop=time_stop,
        dt=td.dt,
        nr_hours=td.hours,
        nr_minutes=td.minutes,
        manual=True,
        project=proj
        )
    database.add_object(tlog)

def get_total_time_for_day(dtime: datetime.datetime, include_ongoing: bool = True) -> utils.TimeDelta | None:
    tlogs = database.get_time_logs_for_day(dtime)
    if not tlogs:
        return None
    return _get_total_time_for_time_logs(tlogs, include_ongoing=include_ongoing)


def get_total_time_for_project_and_day(proj: Project, dtime: datetime.datetime, include_ongoing: bool = True) -> utils.TimeDelta | None:
    tlogs = database.get_project_time_logs_for_day(proj, dtime)
    if not tlogs:
        return None
    return _get_total_time_for_time_logs(tlogs, include_ongoing=include_ongoing)


def get_total_time_for_project_and_week(proj: Project, week_number: str | int, include_ongoing: bool = True) -> utils.TimeDelta | None:
    tlogs = database.get_project_time_logs_for_week(proj, week_number)
    if not tlogs:
        return None
    return _get_total_time_for_time_logs(tlogs, include_ongoing=include_ongoing)


def _get_total_time_for_time_logs(tlogs: list[TimeLog], include_ongoing: bool = True) -> utils.TimeDelta | None:
    if not tlogs:
        return None
    time_delta = datetime.timedelta()
    for tlog in tlogs:
        dt = tlog.dt
        if not dt:
            if not include_ongoing:
                continue
            dt = datetime.datetime.now() - tlog.time_start
        time_delta += dt
    return utils.TimeDelta(time_delta)

