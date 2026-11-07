from fastapi import FastAPI, HTTPException
from routers.users import router as user_router
from routers.courses import router as courses_router
from routers.enrollments import router as enrollments_router
from database import lifespan, pool

app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(courses_router)
app.include_router(enrollments_router)


@app.get("/health-check")
def health_check():
    try:
        with pool.connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS ok;")

                result = cursor.fetchone()

                if result["ok"] != 1:
                    raise HTTPException(
                        status_code=503,
                        detail="Database health check failed"
                    )
                
    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database Unavailabe"
        )from exc

    return {
            "Status" : "Healthy",
            "database" : "Connected"
        }

# Student search feature development