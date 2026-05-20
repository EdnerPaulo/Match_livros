from fastapi import FastAPI
from app.controllers.main import router
from app.models.database import init_db

app = FastAPI(title="API Biblioteca Digital")

# Inicializa o banco no Neon
init_db()

app.include_router(router)