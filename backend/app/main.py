from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import standards, chat

app = FastAPI(
    title="BIS Navigator API",
    description="AI-powered assistant for BIS Standards and Services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(standards.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {
        "message": "BIS Navigator API is running",
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }