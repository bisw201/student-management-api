from fastapi import APIRouter, HTTPException, Depends
from database import pool
from pydantic import BaseModel, field_validator, model_validator, ConfigDict
from psycopg.errors import UniqueViolation
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy_database import get_db
from models import Course, Student, Enrollments

router = APIRouter(prefix="/courses", tags=["Courses"])

class CreateCourse(BaseModel):
    title : str
    description : str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value:str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Title cannot be empty")
        return value

class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id : int
    title : str
    description : str | None = None

class UpdateCourse(BaseModel):
    title : str | None = None
    description : str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None:
            value = value.strip()
            if not value:
                raise ValueError("Title cannot be empty")
        return value

    @model_validator(mode="after")
    def check_fields(self):
        if self.title is None and self.description is None:
            raise ValueError("Provide at least one field to update")
        return self

@router.post("/create-courses",response_model=CourseResponse)
def create_course(course : CreateCourse):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('''INSERT INTO courses (title, description) 
                VALUES (%s, %s) RETURNING id, title, description;''',
                (course.title, course.description))

                new_course = cursor.fetchone()

    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail= "title already exists."
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error"
        ) from exc

    return new_course

@router.get("/fetch-course", response_model=list[CourseResponse])
def fetch_course():
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, title, description FROM courses ORDER BY id;")

                all_courses = cursor.fetchall()

    except Exception as exc: 
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc

    return all_courses

@router.get("/get-course-by-id", response_model=CourseResponse)
def get_course_by_id(id:int):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('''Select id, title, description from courses where id = %s;''',(id,))

                fetched_course = cursor.fetchone()
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )

    if fetched_course is None:
        raise HTTPException(
            status_code=404,
            detail="Course Not Found"
        )

    return fetched_course

@router.patch("/update-course", response_model=CourseResponse)
def update_course(course_id:int , course : UpdateCourse):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                                UPDATE courses
                                SET title = COALESCE(%s, title),
                                    description = COALESCE(%s, description)
                                WHERE id = %s
                                RETURNING id, title, description;""",
                                (course.title,course.description, course_id))

                updated_course = cursor.fetchone()
        
    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="title already exists"
        ) from exc
    
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc
    
    if updated_course is None :
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return updated_course


@router.delete("/delete-course",response_model=CourseResponse)
def delete_course(course_id : int):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(''' DELETE FROM courses WHERE id = %s 
                RETURNING id, title, description;''', (course_id,))
            
                deleted_course = cursor.fetchone()
    
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc

    if deleted_course is None:
        raise HTTPException(
            status_code=404,
            detail="Course Not Found"
        )

    return deleted_course

@router.get("/fetch-courses-orm", response_model=list[CourseResponse])
def fetch_course_orm(db : Session = Depends(get_db)):
    try:
        statement = select(Course).order_by(Course.id)

        course = db.scalars(statement).all()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )

    return course

@router.get("/fetch-courses-orm-by-id", response_model=CourseResponse)
def fetch_course_orm_by_id(course_id : int ,db : Session = Depends(get_db)):
    try:
        # statement = select(Course).where(     --> This can be replaced by a simplier method
        #     Course.id == course_id
        # )

        # course = db.scalar(statement)

        course = db.get(Course, course_id)          # --> It provides a simplier way to fetch primary key 

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course Not Found"
        )

    return course

@router.post("/create-course-orm", response_model=CourseResponse)
def create_course_orm(new_course : CreateCourse, db:Session = Depends(get_db)):
    try:
        add_course = Course(
            title = new_course.title,
            description = new_course.description
        )

        db.add(add_course)
        db.commit()
        db.refresh(add_course)

        return add_course
    
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Course title already exists or violates a database constraint."
        )from exc

@router.patch("/update-course-orm", response_model=CourseResponse)
def update_course_orm(course_id : int, updated_course : UpdateCourse, db : Session = Depends(get_db)):
    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course Not found"
        )
    try:
        update_data = update_course.model_dump(exclude_unset = True)

        for field, value in update_data.items():
            setattr(course, field, value)

        db.commit()
        db.refresh(course)

        return course

    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Course title already exists or Database constraint violates."
        )from exc


@router.delete("/delete-course-orm", response_model=CourseResponse)
def delete_course_orm(course_id : int, db : Session = Depends(get_db)):
    course = db.get(Course, course_id)

    if course is None:
        raise HTTPException(
            status_code=404,
            detail= "Course not found"
        )

    course_data = CourseResponse.model_validate(course)

    db.delete(course)
    db.commit()

    return course_data

@router.get("/{student-id}/enrollments")
def get_student_enrollment(student_id : int, db : Session = Depends(get_db)):
    try:
        statement = (
            select(Student).options(
                joinedload(Student.enrollments).joinedload(Enrollments.course)
            ).where(Student.id == student_id)
        )

        student = db.scalar(statement).unique().first()

        if not student:
            raise HTTPException(
                status_code=404,
                detail="Student not exists"
            )

        return[
            {
                "enrollment_id": enrollment.id,
                "course_id": enrollment.course.id,
                "course_title": enrollment.course.title,
                "description": enrollment.course.description
            }
            for enrollment in student.enrollments
        ]

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )

@router.get("/{given_course_id}/course-with-all-enrolled-students")
def course_enrolled_students(given_course_id : int, db : Session = Depends(get_db)):
    try:

        course = db.get(Course, given_course_id)

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found"
            )

        statement = (select(Student).join(Student.enrollments).where(Enrollments.course_id == given_course_id))

        students = db.scalars(statement).unique().all()

        return[
            {
                "name" : student.name,
                "email" : student.email,
                "age" : student.age,
            }
            for student in students
        ]

    except HTTPException:
        raise
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )
