from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.database.database import engine, Base
from backend.routers import auth, cart, orders, uploads, admin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Replione API V2")

from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(uploads.router)
app.include_router(admin.router)

# Mount frontend
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/images", StaticFiles(directory="frontend/images"), name="images")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")

@app.get("/admin")
@app.get("/admin/")
def serve_admin():
    return FileResponse("frontend/admin.html")

@app.get("/{page}.html")
def serve_html(page: str):
    return FileResponse(f"frontend/{page}.html")
