"""Main module to execute FastAPI"""

import secure
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import healtcheck
from app.api.api_v1 import api_router

secure_headers = secure.Secure()

tags_metadata = [
    {
        "name": "Auth",
        "description": "Autenticación y autorización de usuarios",
    },
]

fastapi_app = FastAPI(
    title="FastAPI SQL/DB Boilerplate",
    description="Boilerplate para proyectos con FastAPI y SQL",
    contact={
        "name": "Christian Gutierrez Varela",
        "url": "https://www.linkedin.com/in/christian-gutierrez-371973176/",
        "email": "christiangtzv@gmail.com",
    },
    openapi_tags=tags_metadata,
)


# Cors middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["PUT", "GET", "POST", "DELETE"],
    allow_headers=["*"],
)


@fastapi_app.middleware("http")
async def set_secure_headers(request, call_next):
    """
    Secure headers middleware
    """
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response


fastapi_app.include_router(api_router, prefix="/api/v1")
fastapi_app.include_router(healtcheck.router, prefix="/api/v1")

app = fastapi_app
