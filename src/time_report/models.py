import datetime
import pathlib

from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    contact: str | None
    project_number: int | None
    kst: int | None
    hours_in_plan: int | None
    color: str | None
    comment: str = Field(default='')

    timelogs: list["TimeLog"] = Relationship(back_populates="project")
    timesubmits: list["TimeSubmit"] = Relationship(back_populates="project")


class TimeLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    time_start: datetime.datetime
    time_stop: datetime.datetime | None
    dt: datetime.timedelta | None
    nr_hours: int | None
    nr_minutes: int | None
    manual: bool = Field(default=False)
    comment: str = Field(default='')

    project_id: int = Field(foreign_key="project.id")
    project: Project = Relationship(back_populates="timelogs")


class TimeSubmit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime.date
    nr_hours: int
    comment: str = Field(default='')

    project_id: int = Field(foreign_key="project.id")
    project: Project = Relationship(back_populates="timesubmits")


class DateInfo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime.date = Field(unique=True)
    time_in_plan: datetime.timedelta
    comment: str = Field(default='')


home_dir = pathlib.Path().home() / 'time_report'
home_dir.mkdir(parents=True, exist_ok=True)
sqlite_file_name = str(home_dir / "time_report.sqlite")
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def add_objects(*args: SQLModel) -> None:
    with Session(engine) as session:
        session.add_all(args)
        session.commit()


def add_sample_data():
    with Session(engine) as session:
        admin = Project(name="Administration")
        nodc = Project(name="NODC", hours_in_plan=350)
        ifcb = Project(name="IFCB")
        session.add(admin)
        session.add(nodc)
        session.add(ifcb)
        session.commit()

        session.refresh(admin)
        session.refresh(nodc)
        session.refresh(ifcb)

        pasta = ItemType(name="pasta", manufacturer='barilla', category=food)
        krossad_tomat = ItemType(name="krossad tomat", manufacturer='ica', category=food)
        train = ItemType(name="tågbana", manufacturer='brio', category=toys)
        session.add(pasta)
        session.add(krossad_tomat)
        session.add(train)
        session.commit()


if __name__ == "__main__":
    create_db_and_tables()

    with Session(engine) as session:
        statement = select(Project, ItemType).join(ItemType)
        results = session.exec(statement)
        for cat, item_type in results:
            print("Cat:", cat, "IT:", item_type)
