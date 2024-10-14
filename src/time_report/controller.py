from time_report import database
from time_report.models import Project, TimeLog, DateInfo, TimeSubmit
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


def get_total_time_for_project(proj: Project, time_stop: datetime.date, include_ongoing: bool = True) -> utils.TimeDelta | None:
    tlogs = database.get_project_time_logs(proj, time_stop)
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


def get_date_info(date: datetime.date) -> DateInfo:
    date_stop = date
    return database.get_dates_info(date, date_stop)[0]


def get_dates_info(date_start: datetime.date | None = None, date_stop: datetime.date | None = None) -> list[DateInfo]:
    return database.get_dates_info(date_start, date_stop)


def set_info_for_dates(*lst: dict) -> None:
    year = datetime.datetime.now().year
    red_dates = utils.get_red_dates(year)
    objs = []
    for item in lst:
        date = item['date']
        if date.weekday() in [5, 6] or date in red_dates:
            continue
        info = database.get_date_info(date)
        time_in_plan = datetime.timedelta(hours=item.get('nr_hours', 0))
        info.time_in_plan = time_in_plan
        objs.append(info)
    database.add_objects(*objs)


def set_week_info_from_date(date: datetime.date, *lst: dict) -> None:
    mapping = {}
    for item in lst:
        mapping[item['date'].weekday()] = item
    year = datetime.datetime.now().year
    all_dates_info = []
    while date.year == year:
        mapped_date_info = mapping[date.weekday()]
        date_info = dict(
            date=date,
            nr_hours=mapped_date_info.get('nr_hours', 0)
        )
        all_dates_info.append(date_info)
        date = date + datetime.timedelta(days=1)
    set_info_for_dates(*all_dates_info)


def get_sum_of_scheduled_time(date_start: datetime.date = None, date_stop: datetime.date = None) -> datetime.timedelta:
    infos = database.get_dates_info(date_start=date_start, date_stop=date_stop)
    dt = datetime.timedelta()
    for info in infos:
        if not info.time_in_plan:
            continue
        dt += info.time_in_plan
    return dt


def get_sum_of_submitted_time(date_stop: datetime.date, proj: Project = None) -> datetime.timedelta:
    subs = database.get_time_submits(date_stop=date_stop, proj=proj)
    dt = datetime.timedelta()
    for sub in subs:
        if not sub.nr_hours:
            continue
        dt += sub.nr_hours
    return dt


def get_latest_submitted_time() -> TimeSubmit | None:
    subs = database.get_time_submits()
    if not subs:
        return
    return subs[-1]


def add_default_date_info() -> None:
    if database.get_dates_info():
        return
    year = datetime.datetime.now().year
    red_dates = utils.get_red_dates(year)
    start_datetime = datetime.datetime(year, 1, 1)
    dinfos = []
    for d in range(366):
        dtime = start_datetime + datetime.timedelta(days=d)
        non_working_day = False
        if dtime.weekday() in [5, 6] or dtime.date() in red_dates:
            non_working_day = True
        dinfo = DateInfo(
            date=dtime.date(),
            week_day_number=dtime.weekday(),
            non_working_day=non_working_day,
        )
        dinfos.append(dinfo)
    database.add_objects(*dinfos)


