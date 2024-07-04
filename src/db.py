from sqlmodel import Session, SQLModel, create_engine

from src.settings import settings

engine = create_engine(settings.database_uri)


def create_all():
    SQLModel.metadata.create_all(engine)


def drop_all():
    SQLModel.metadata.drop_all(engine)


def with_db_session(fn):
    def db_session_wrapper(*args, **kwargs):
        with Session(engine) as session:
            kwargs["db_session"] = session
            return fn(*args, **kwargs)

    return db_session_wrapper
