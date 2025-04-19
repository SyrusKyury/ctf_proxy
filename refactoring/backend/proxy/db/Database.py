from sqlmodel import create_engine, Session


class Database:
    _engine = None

    @classmethod
    def initialize(cls, db_url: str, echo: bool = False):
        if cls._engine is None:
            cls._engine = create_engine(db_url, echo=echo)

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            raise RuntimeError("The database has not been initialized.")
        return cls._engine

    @classmethod
    def get_session(cls) -> Session:
        if cls._engine is None:
            raise RuntimeError("The database has not been initialized.")
        return Session(cls._engine)
