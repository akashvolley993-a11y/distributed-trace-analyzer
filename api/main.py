"""FastAPI Application Entrypoint (Member 3)."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routes import router

load_dotenv()

app = FastAPI(
    title="Distributed Trace & RCA Platform API (Member 3)",
    description=(
        "Backend API integrating Member 1 (Distributed Traces & Dependencies) "
        "and Member 2 (Regression Detection & Evidence) with LangGraph RCA Agent "
        "and Streamlit Dashboard."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Streamlit frontend and local browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting server on http://{host}:{port}")
    uvicorn.run("api.main:app", host=host, port=port, reload=True)
