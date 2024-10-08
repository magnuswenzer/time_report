import datetime

from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship

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


def get_projects() -> list[Project]:
    with Session(engine) as session:
        statement = select(Project)
        return list(session.exec(statement))


def get_time_logs_for_project(proj: Project) -> list[TimeLog]:
    with Session(engine) as session:
        statement = select(TimeLog).where(TimeLog.project_id==proj.id)
        return list(session.exec(statement))


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
        statement = select(Project)
        results = session.exec(statement)
        for proj in results:
            print(type(proj), proj)
