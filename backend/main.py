import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from backend.database import Base, engine, SessionLocal
from backend.seed_data import seed_demo_data

# Import all API routers
from backend.routers import (
    auth,
    providers,
    menu,
    ratings,
    hygiene,
    availability,
    advertisements,
    chat,
    notifications
)


def init_database():
    """Ensures database tables are created and initial demo data is seeded."""
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_demo_data(db)
        finally:
            db.close()
    except Exception as e:
        print(f"[DATABASE INIT ERROR] {e}")


# Initialize immediately upon import so tables exist for test clients & scripts
init_database()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events:
    """
    init_database()
    yield
    print("[SERVER SHUTDOWN] Application shutting down cleanly.")


app = FastAPI(
    title="CEP Tiffin Services API",
    description="Full-stack college Community Engagement Project (CEP) connecting students and local tiffin providers.",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for local development and demonstration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all modular routers  (MUST come before any static mounts)
app.include_router(auth.router)
app.include_router(providers.router)
app.include_router(menu.router)
app.include_router(ratings.router)
app.include_router(hygiene.router)
app.include_router(availability.router)
app.include_router(advertisements.router)
app.include_router(chat.router)
app.include_router(notifications.router)


@app.get("/api/health")
def health_check():
    """
    Simple health check endpoint to verify backend server status.
    """
    return {
        "status": "online",
        "project": "CEP Tiffin Services (Khane ki Khoj)",
        "framework": "FastAPI",
        "database": "PostgreSQL / SQLAlchemy"
    }


# Ensure uploads directories exist
os.makedirs("uploads/hygiene", exist_ok=True)
os.makedirs("uploads/advertisements", exist_ok=True)
os.makedirs("uploads/ratings", exist_ok=True)

# Mount uploads directory for static image serving
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Mount CSS/JS/assets as static (safe — these paths never overlap with /api/*)
if os.path.exists("frontend/css"):
    app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
if os.path.exists("frontend/js"):
    app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
if os.path.exists("frontend/images"):
    app.mount("/images", StaticFiles(directory="frontend/images"), name="images")
if os.path.exists("frontend/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")


# Catch-all: serve frontend HTML pages by filename (e.g. /login.html, /reset-password.html)
# This is registered LAST so it never shadows any API route above.
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str, request: Request):
    """Serve frontend HTML files. Falls back to index.html for SPA-style navigation."""
    frontend_dir = os.path.abspath("frontend")

    # Direct file match (e.g., login.html, reset-password.html)
    candidate = os.path.join(frontend_dir, full_path)
    if os.path.isfile(candidate):
        return FileResponse(candidate)

    # Root → index.html
    if full_path in ("", "/"):
        index = os.path.join(frontend_dir, "index.html")
        if os.path.isfile(index):
            return FileResponse(index)

    # Fallback: try appending .html
    candidate_html = candidate + ".html"
    if os.path.isfile(candidate_html):
        return FileResponse(candidate_html)

    # Final fallback → index.html
    index = os.path.join(frontend_dir, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)

    return HTMLResponse("<h1>404 – Page not found</h1>", status_code=404)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
