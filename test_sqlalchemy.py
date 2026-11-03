from sqlalchemy import select

from models import Course
from sqlalchemy_database import SessionLocal

# with SessionLocal() as session:
#     statement = select(Course).order_by(Course.id)

#     courses = session.scalars(statement).all()

#     for course in courses:
#         print(course.id, course.title, course.description)


#     add_course = Course(
#         title= "SqlAlchemy Fundamentals",
#         description= "Learning how orm works"
#     )

#     session.add(add_course)

#     session.commit()

#     session.refresh(add_course)

#     print(f"Newly added Course : "
#           f"{add_course.id}, {add_course.title}, {add_course.description}")

#     new_statement = select(Course).order_by(Course.id)
#     courses = session.scalars(new_statement).all()

#     print("\nAll Courses : ")
#     for course in courses:
#         print(course.id, course.title, course.description)

with SessionLocal() as session:

    statement = select(Course).where(
        Course.title == "SqlAlchemy Fundamentals"
    )

    course = session.scalar(statement)

    if course is None:
        print("Course not found")
    else:
        session.delete(course)
        session.flush()
        print("Deletion demonstrated!! but not commited")
        session.rollback()

# with SessionLocal() as session:

#     statement = select(Course).order_by(Course.id)

#     courses = session.scalars(statement).all()

#     for course in courses:
#         print(course.id, course.title, course.description)
