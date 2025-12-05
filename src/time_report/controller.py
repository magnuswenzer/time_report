from time_report import database
from time_report.models import Project, TimeLog, DateInfo, TimeSubmit, WeekInfo
import datetime
from time_report import utils
import yaml
from time_report.settings import settings


def start_logging(proj: Project | str) -> None:
    stop_logging()
    now = datetime.datetime.now()
    if now.year != settings.year:
        print(f'You can start logging on year {settings.year}')
        return
    if type(proj) == str:
        obj = database.get_project(proj, year=settings.year)
        if not obj:
            raise KeyError(f'Invalid project {proj}')
        proj = obj
    tlog = TimeLog(
        time_start=now,
        project=proj
    )
    database.add_object(tlog)


def stop_logging() -> None:
    # tlog = database.get_running_time_log(year=settings.year)
    tlog = database.get_running_time_log()
    if not tlog:
        return
    tlog.time_stop = datetime.datetime.now()
    td = utils.TimeDelta(tlog.time_stop - tlog.time_start)
    tlog.dt = td.dt
    tlog.nr_hours = td.hours
    tlog.nr_minutes = td.minutes
    database.add_object(tlog)


def add_manual_time_to_project(proj: Project, time_start: datetime.datetime, nr_minutes: int | str, comment: str = '') -> None:
    print(f"{nr_minutes=}")
    print(f"{time_start=}")
    print(f"{datetime.timedelta(minutes=int(nr_minutes))=}")
    time_stop = time_start + datetime.timedelta(minutes=int(nr_minutes))
    print(f"{time_stop=}")
    td = utils.TimeDelta(time_stop - time_start)
    print(f"{td=}")
    print(f"{td.hours=}")
    print(f"{td.minutes=}")
    print(f"{td.dt=}")

    tlog = TimeLog(
        time_start=time_start,
        time_stop=time_stop,
        dt=td.dt,
        nr_hours=td.hours,
        nr_minutes=td.minutes,
        manual=True,
        project=proj,
        comment=comment,
        )
    database.add_object(tlog)


def get_all_time_logs_for_project(proj: Project,
                                  date_stop: datetime.date = None) -> list[TimeLog]:
    date_stop = date_stop or settings.last_date_of_year
    tlogs = database.get_project_time_logs(settings.year,
                                           proj,
                                           date_start=settings.first_date_of_year,
                                           date_stop=date_stop,
                                           )
    return tlogs


def get_all_vab_time_logs() -> list[TimeLog]:
    proj = database.get_project('VAB', year=settings.year)
    tlogs = get_all_time_logs_for_project(proj)
    return sorted(tlogs, key=lambda x: x.time_start)


def get_total_time_for_day(dtime: datetime.datetime, include_ongoing: bool = True) -> utils.TimeDelta | None:
    tlogs = database.get_time_logs_for_day(dtime)
    if not tlogs:
        return None
    return _get_total_time_for_time_logs(tlogs, include_ongoing=include_ongoing)


def get_total_time_for_project(proj: Project,
                               date_stop: datetime.date = None,
                               include_ongoing: bool = True) -> utils.TimeDelta:
    #print('='*100)
    tlogs = get_all_time_logs_for_project(proj, date_stop=date_stop)
    # tlogs = database.get_project_time_logs(settings.year,
    #                                        proj,
    #                                        date_start=settings.gt,
    #                                        date_stop=date_stop)
    #print(f'{proj=}   :   {date_stop=}   :   {len(tlogs)}   :   {tlogs}')
    #print('-' * 100)
    if not tlogs:
        return utils.TimeDelta()
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


def get_total_submitted_time_for_project_and_week(proj: Project,
                                                  week_number: str | int) -> utils.TimeDelta | None:
    weekdays = utils.get_week_range(week_number)
    tlogs = database.get_time_submits(date_start=weekdays[0],
                                      date_stop=weekdays[-1],
                                      proj=proj)
    if not tlogs:
        return None
    return _get_total_time_for_time_submits(tlogs)


def get_total_time_for_week(week_number: str | int) -> utils.TimeDelta | None:
    week_dates = utils.get_week_dates(week_number)
    last_date = min([datetime.datetime.now().date(), week_dates[-1]])
    worked_time = get_sum_of_worked_time(date_start=week_dates[0],
                                         date_stop=last_date)
    return worked_time


def _get_total_time_for_time_logs(tlogs: list[TimeLog],
                                  include_ongoing: bool = True) -> utils.TimeDelta | None:
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


def _get_total_time_for_time_submits(tlogs: list[TimeSubmit]) -> utils.TimeDelta | None:
    if not tlogs:
        return None
    time_delta = datetime.timedelta()
    for tlog in tlogs:
        dt = tlog.submitted_time
        time_delta += dt
    return utils.TimeDelta(time_delta)


def get_date_info(date: datetime.date) -> DateInfo:
    date_stop = date
    return database.get_dates_info(date, date_stop)[0]


def get_dates_info(date_start: datetime.date | None = None, date_stop: datetime.date | None = None) -> list[DateInfo]:
    return database.get_dates_info(date_start, date_stop)


def get_week_info(week_nr: int) -> WeekInfo | None:
    return database.get_week_info(week_nr, settings.year)


def get_work_percentage_for_week(week_nr: int) -> int:
    winfo = get_week_info(week_nr)
    if not winfo:
        return 100
    return winfo.work_percentage


def set_info_for_dates(*lst: dict) -> None:
    year = settings.year
    red_dates = utils.get_red_dates().get_dates(year)
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


def set_info_for_week(week_info: dict) -> None:
    info = database.get_week_info(week_info['week_nr'], settings.year)
    if not info:
        info = WeekInfo()
    info.year = settings.year
    info.week_number = week_info['week_nr']
    info.work_percentage = week_info['work_percentage']
    database.add_object(info)


def set_week_info_from_week(from_week: int | str, week_info: dict) -> None:
    for week in utils.get_weeks_for_year(settings.year):
        if week.week < from_week:
            continue
        week_info['week_nr'] = week.week
        set_info_for_week(week_info)


def set_week_info_from_date(date: datetime.date, *lst: dict) -> None:
    mapping = {}
    for item in lst:
        mapping[item['date'].weekday()] = item
    year = settings.year
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


def get_sum_of_worked_time(date_start: datetime.date = None,
                           date_stop: datetime.date = None,
                           include_ongoing: bool = True) -> utils.TimeDelta:
    date_start = date_start or settings.first_date_of_year
    logs = database.get_time_logs(date_start=date_start,
                                  date_stop=date_stop,
                                  include_ongoing=include_ongoing)
    dt = datetime.timedelta()
    for lo in logs:
        if not lo.dt:
            continue
        dt += lo.dt
    return utils.TimeDelta(dt)


def get_sum_of_scheduled_time(date_start: datetime.date = None, date_stop: datetime.date = None) -> utils.TimeDelta:
    red_dates = utils.get_red_dates().get_dates(settings.year)
    dt = datetime.timedelta()

    date_start = date_start or settings.first_date_of_year
    date_stop = date_stop or datetime.datetime.now().date()

    for date in utils.get_date_range(date_start, date_stop):
        if date in red_dates:
            continue
        if date.weekday() in [5, 6]:
            continue
        week = utils.get_week_for_date(date)
        percent = get_work_percentage_for_week(week.week)
        dt = dt + (datetime.timedelta(hours=8) * percent / 100)
    return utils.TimeDelta(dt)


def get_sum_of_scheduled_time_for_week(week: int) -> utils.TimeDelta:
    dates = utils.get_week_dates(week)
    dates = [date for date in dates if date.year == settings.year]
    return get_sum_of_scheduled_time(dates[0], dates[-1])


def get_sum_of_scheduled_time_per_day(date_start: datetime.date = None, date_stop: datetime.date = None) -> dict[str | int, datetime.timedelta]:
    infos = database.get_dates_info(date_start=date_start, date_stop=date_stop)
    days = {}
    dt = datetime.timedelta()
    for info in infos:
        if not info.time_in_plan:
            continue
        days.setdefault(info.week_day_number, datetime.timedelta())
        days[info.week_day_number] += info.time_in_plan
        dt += info.time_in_plan
    days['tot'] = dt
    return days


def get_sum_of_submitted_time(date_start: datetime.date = None, date_stop: datetime.date = None, proj: Project = None) -> utils.TimeDelta:
    date_start = date_start or settings.first_date_of_year
    subs = database.get_time_submits(date_start=date_start, date_stop=date_stop, proj=proj)
    dt = datetime.timedelta()
    for sub in subs:
        if not sub.submitted_time:
            continue
        dt += sub.submitted_time
    return utils.TimeDelta(dt)


def get_latest_submitted_time() -> TimeSubmit | None:
    subs = database.get_time_submits()
    if not subs:
        return
    return subs[-1]


def get_latest_date_in_database() -> datetime.date | None:
    return database.get_latest_date_in_database()


def get_time_submit(proj_name: str, date: datetime.date) -> TimeSubmit:
    proj = database.get_project(proj_name, year=settings.year)
    return database.get_time_submit(proj=proj, date=date)


def submit_time(proj_name: str, date: datetime.date, nr_hours: int):
    sub = get_time_submit(proj_name, date)
    if sub and sub.is_reported:
        raise Exception(f'Already reported with {sub.submitted_time} hours: {proj_name} ({date})')
    dt = datetime.timedelta(hours=nr_hours)
    if sub:
        sub.submitted_time = dt
    else:
        proj = database.get_project(proj_name, year=settings.year)
        sub = database.TimeSubmit(
            project=proj,
            date=date,
            submitted_time=dt,
            report_date=datetime.datetime.now().date()
        )
    database.add_object(sub)


def mark_as_reported(proj_name: str, date: datetime.date):
    sub = get_time_submit(proj_name, date)
    if not sub:
        raise Exception(f'No submit found: {proj_name} ({date})')
    if sub and sub.is_reported:
        raise Exception(f'Already reported with {sub.submitted_time} hours: {proj_name} ({date})')
    sub.is_reported = True
    database.add_object(sub)


def add_default_date_info() -> None:
    # if database.get_dates_info():
    #     return
    # year = settings.year
    # red_dates = utils.get_red_dates().get_dates(year)
    red_dates = utils.get_red_dates().get_dates()
    # start_datetime = datetime.datetime(year, 1, 1)
    start_date = utils.get_first_date_of_week(1)
    dinfos = []
    for d in range(375):
        dtime = start_date + datetime.timedelta(days=d)
        non_working_day = False
        if dtime.weekday() in [5, 6] or dtime in red_dates:
            non_working_day = True
        dinfo = database.get_date_info(dtime)
        if not dinfo:
            dinfo = DateInfo()
        dinfo.date = dtime
        dinfo.week_day_number = dtime.weekday()
        dinfo.non_working_day = non_working_day

        dinfos.append(dinfo)
    database.add_objects(*dinfos)


def update_red_dates():
    red_dates = utils.get_red_dates().get_dates()
    database.update_red_dates(red_dates)


def update_comment_in_time_log(_id: int, comment: str) -> None:
    tlog = database.get_time_log_by_id(_id)
    tlog.comment = comment
    database.add_object(tlog)

def get_projects():
    return list(database.get_projects(year=settings.year))


if __name__ == '__main__':
    update_red_dates()


