from fastapi import HTTPException,APIRouter
from pydantic import BaseModel,model_validator
from database import pool
from psycopg.errors import UniqueViolation

router = APIRouter(prefix="/users",tags=["Users"])

class StudentResponse(BaseModel):
    id : int
    name : str
    email : str
    age : int

class CreateStudent(BaseModel):
    name : str
    email : str
    age : int

class UpdateStudent(BaseModel):
    name : str | None = None
    email : str | None = None
    age : int | None = None

    @model_validator(mode="after")
    def check_fields(self):
        if all(getattr(self, field) is None for field in ("name", "email", "age")):
            raise ValueError("Provide atleast one field to update")
        return self


@router.get("/get-users")
def get_users():
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * from users order by id;")
            new_row = cursor.fetchall()

    return {"users" : new_row}

    
@router.get("/get-user-by-id")
def get_user_by_id(id:int):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('''Select * from users where id = %s;''',(id,))

                fetched_user = cursor.fetchone()
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )

    if fetched_user is None:
        raise HTTPException(
            status_code=404,
            detail="User Not Found"
        )

    return {"user":fetched_user}

@router.post("/create-users", response_model=StudentResponse)
def create_users(student:CreateStudent):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, email, age)
                    VALUES (%s, %s, %s)
                    RETURNING id, name, email, age;
                    """, (student.name, student.email, student.age))

                new_student = cursor.fetchone()
                
        return new_student
    

    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc

@router.patch("/update-user", response_model=StudentResponse)
def update_user(user_id:int , student : UpdateStudent):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                                UPDATE users
                                SET name = COALESCE(%s, name),
                                email = COALESCE(%s,email),
                                age = COALESCE(%s,age)
                                WHERE id = %s
                                RETURNING id, name, email, age;""",
                                (student.name, student.email, student.age, user_id))

                updated_student = cursor.fetchone()
        
    except UniqueViolation as exc:
        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        ) from exc
    
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc
    
    if updated_student is None :
        raise HTTPException(
            status_code=404,
            detail="Student not found"
        )

    return updated_student

@router.delete("/delete-user",response_model=StudentResponse)
def delete_user(user_id : int):
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(''' DELETE FROM users WHERE id = %s 
                RETURNING id, name, email, age;''', (user_id,))
            
                deleted_student = cursor.fetchone()
    
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        ) from exc

    if deleted_student is None:
        raise HTTPException(
            status_code=404,
            detail="User Not Exists"
        )

    return deleted_student
    