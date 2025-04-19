from sqlmodel import Field, SQLModel
from .ServiceType import ServiceType
from sqlalchemy import Enum as SQLAlchemyEnum


class Service(SQLModel, table=True):
    id : int | None = Field(default=None, primary_key=True)
    name : str = Field(index=True)
    port : int
    type: ServiceType = Field(sa_column=Field(
        sa_column = SQLAlchemyEnum(ServiceType, name="service_type_enum")
    ))