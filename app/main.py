from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.lms.trigger import router as trigger_router
from app.lms.entry_result import router as entry_result_router
from app.lms.entry_status import router as entry_status_router

from app.routes.sdk_commands import router as sdk_commands_router
from app.routes.sdk_ingest import router as sdk_ingest_router

app = FastAPI(title="LabGuard AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UI_DIR = os.path.join(os.path.dirname(__file__), "ui")
app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")

# LMS routes
app.include_router(trigger_router, prefix="/lms")
app.include_router(entry_result_router, prefix="/lms")
app.include_router(entry_status_router, prefix="/lms")  

# SDK routes
app.include_router(sdk_commands_router, prefix="/sdk")
app.include_router(sdk_ingest_router, prefix="/sdk")

@app.get("/")
def health():
    return {"status": "LabGuard running"}
