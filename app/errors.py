from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


async def http_exception_handler(
  request: Request,
  exc: HTTPException,
):
  if isinstance(exc.detail, dict):
    code = exc.detail.get("error", "HTTP_ERROR")
    message = exc.detail.get("message", "Request failed.")
  else:
    code = "HTTP_ERROR"
    message = str(exc.detail)

  return JSONResponse(
    status_code=exc.status_code,
    content={
      "error": {
        "code": code,
        "message": message,
      }
    },
    headers=exc.headers,
  )


async def validation_exception_handler(
  request: Request,
  exc: RequestValidationError,
):
  return JSONResponse(
    status_code=422,
    content=jsonable_encoder({
      "error": {
        "code": "VALIDATION_ERROR",
        "message": "The request contains invalid data.",
        "details": exc.errors(),
      }
    }),
  )
