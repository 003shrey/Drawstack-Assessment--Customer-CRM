from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .database import Base, engine
from .routers.tickets import router as tickets_router

BASE_DIR = Path(__file__).resolve().parent

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Support CRM API", version="1.0.0")

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

templates = Jinja2Templates(directory=BASE_DIR / "templates")
app.include_router(tickets_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
        })

    return JSONResponse(
        status_code=422,
        content={"detail": "Validation failed", "errors": errors},
    )


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/create", response_class=HTMLResponse)
def create_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="create.html",
    )


@app.get("/tickets/{ticket_id}", response_class=HTMLResponse)
def detail_page(request: Request, ticket_id: str):
    return templates.TemplateResponse(
        request=request,
        name="detail.html",
        context={"ticket_id": ticket_id},
    )


@app.get("/health")
def health():
    return {"status": "ok"}
