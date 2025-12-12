from fastapi import FastAPI, Request
from app.routes import router  # import the router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from utils.db import Base, engine

import app.models

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Loan Eligibility API")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):

    errors = exc.errors()
    missing_fields = []

    for error in errors:
        if error["type"] == "missing":
            missing_fields.append(error["loc"][-1])

    if missing_fields:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": ", ".join(missing_fields) + " are required"
            }
        )

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "message": "Invalid input",
            "details": errors
        }
    )


# Include the routes from routes.py
app.include_router(router)