from fastapi import FastAPI
from app.controllers.main import router
from app.models.database import init_db
from app.models.database import engine, Base

app = FastAPI(title="API Biblioteca Digital")



# Adicione isso logo antes de iniciar o app FastAPI
Base.metadata.create_all(bind=engine)

# Inicializa o banco no Neon
init_db()

app.include_router(router)
