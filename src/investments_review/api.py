import logging
import os
from mimetypes import guess_extension

import aiofiles
import uvicorn
from starlette.applications import Starlette
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse

from .presentations.workflow import workflow as presentations_workflow
from .shared import FileEvent
from .sheets.workflow import workflow as sheets_workflow


async def home_route(request: Request) -> HTMLResponse:
    async with aiofiles.open("index.html") as f:
        content = await f.read()
    return HTMLResponse(content=content, media_type="text/html")


async def scripts_route(request: Request) -> PlainTextResponse:
    async with aiofiles.open("script.js") as f:
        content = await f.read()
    return PlainTextResponse(content=content, media_type="text/javascript")


async def sheets_workflow_route(request: Request) -> JSONResponse:
    if request.method.lower() != "post":
        raise HTTPException(
            status_code=405, detail=f"Method not allowed: {request.method}"
        )
    async with request.form() as form:
        if isinstance((uploaded_file := form["upload_file"]), UploadFile):
            extension = (
                guess_extension(
                    uploaded_file.headers.get(
                        "Content-Type",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                )
                or ".xlsx"
            )
            file_content = await uploaded_file.read()
            tempfile = await aiofiles.tempfile.NamedTemporaryFile(
                suffix=extension, delete_on_close=False, delete=False
            )
            with open(tempfile.name, "wb") as f:
                f.write(file_content)
            try:
                start_event = FileEvent(
                    file_input=str(tempfile.name), is_source_content=False
                )
                run_result = await sheets_workflow.run(start_event=start_event)
                if run_result.error is None:
                    return JSONResponse(
                        content=run_result.model_dump(),
                        status_code=200,
                        media_type="application/json",
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=run_result.error,
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Internal server error: {e}"
                )
            finally:
                os.remove(str(tempfile.name))
        raise HTTPException(
            status_code=400,
            detail="Bad request: you should provide a multipart form file as an input to this API endpoint.",
        )


async def presentations_workflow_route(request: Request) -> JSONResponse:
    if request.method.lower() != "post":
        raise HTTPException(
            status_code=405, detail=f"Method not allowed: {request.method}"
        )
    async with request.form() as form:
        if isinstance((uploaded_file := form["upload_file"]), UploadFile):
            extension = (
                guess_extension(
                    uploaded_file.headers.get(
                        "Content-Type",
                        "application/pdf",
                    )
                )
                or ".pdf"
            )
            file_content = await uploaded_file.read()
            tempfile = await aiofiles.tempfile.NamedTemporaryFile(
                suffix=extension, delete_on_close=False, delete=False
            )
            with open(tempfile.name, "wb") as f:
                f.write(file_content)
            try:
                start_event = FileEvent(
                    file_input=str(tempfile.name), is_source_content=False
                )
                run_result = await presentations_workflow.run(start_event=start_event)
                if run_result.error is None:
                    return JSONResponse(
                        content=run_result.model_dump(),
                        status_code=200,
                        media_type="application/json",
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail=run_result.error,
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Internal server error: {e}"
                )
            finally:
                os.remove(str(tempfile.name))
        raise HTTPException(
            status_code=400,
            detail="Bad request: you should provide a multipart form file as an input to this API endpoint.",
        )


def main() -> None:
    app = Starlette()
    app.add_route(
        path="/",
        name="Home",
        include_in_schema=False,
        route=home_route,
        methods=["GET"],
    )
    app.add_route(
        path="/script.js", include_in_schema=False, route=scripts_route, methods=["GET"]
    )
    app.add_route(
        path="/sheets",
        include_in_schema=True,
        route=sheets_workflow_route,
        methods=["POST"],
    )
    app.add_route(
        path="/presentations",
        include_in_schema=True,
        route=presentations_workflow_route,
        methods=["POST"],
    )
    logging.info("Starting server on http://0.0.0.0:8000")
    try:
        uvicorn.run(app)
    except KeyboardInterrupt:
        return None
