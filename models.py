from sqlalchemy import String, Text, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name : Mapped[str] = mapped_column(
        String(100),
        nullable= False,
    )

    email : Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )
    age : Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )


    enrollments : Mapped[list["Enrollments"]] = relationship(
        back_populates="user"
    )

class Course(Base):
    __tablename__ = "courses"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable= False,
        unique= True
    )

    description : Mapped[str | None] = mapped_column(
        Text,
        nullable= True
    )

    credits : Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    enrollments : Mapped[list["Enrollments"]] = relationship(
        back_populates="course"
    )

class Enrollments(Base):
    __tablename__ = "enrollments"

    id : Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id : Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    course_id : Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )


    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            name = "enrollments_user_id_course_id_key"
        ),
    )

    user : Mapped["Student"] = relationship(
        back_populates="enrollments"
    )

    course : Mapped["Course"] = relationship(
        back_populates="enrollments"
    )