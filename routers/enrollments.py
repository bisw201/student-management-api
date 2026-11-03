from fastapi import HTTPException,APIRouter
from pydantic import BaseModel
from database import pool
from psycopg.errors import (UniqueViolation, ForeignKeyViolation)

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])

class NewEnrollment(BaseModel):
    user_id : int
    course_id : int

class EnrollmentResponse(BaseModel):
    id : int
    user_id : int
    course_id : int


@router.post("/create-enrollment", response_model=EnrollmentResponse)
def create_enrollment(enrollment : NewEnrollment):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:

                cursor.execute(
                    '''INSERT INTO enrollments (user_id, course_id)
                    VALUES (%s, %s)
                    RETURNING id, user_id, course_id;
                    ''',(enrollment.user_id, enrollment.course_id)
                )

                new_enrollment = cursor.fetchone()

    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="Student is already enrolled in this course"
        ) from exc

    except ForeignKeyViolation as exc:
        raise HTTPException(
            status_code=404,
            detail="Student or course not found"
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc

    return new_enrollment

@router.get("/get-all-enrollments", response_model=list[EnrollmentResponse])
def get_all_enrollments():
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, user_id, course_id FROM enrollments ORDER BY id;")

                all_enrollments = cursor.fetchall()

    except HTTPException :
        raise
    
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )from exc

    return all_enrollments


@router.get("/get-enrollment-by-id", response_model=EnrollmentResponse)
def get_enrollment_by_id(enrollment_id : int):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, user_id, course_id FROM enrollments WHERE id = %s;",(enrollment_id,))

                get_enrollment = cursor.fetchone()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )from exc

    if get_enrollment is None:
        raise HTTPException(
            status_code=404,
            detail="Enrollment not found"
        )

    return get_enrollment

@router.delete("/delete-enrollment", response_model=EnrollmentResponse)
def delete_enrollemnt(enrollment_id : int):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM enrollments WHERE id = %s RETURNING id, user_id, course_id;", (enrollment_id,))

                deleted_enrollment = cursor.fetchone()

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc

    if deleted_enrollment is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )
    return deleted_enrollment

