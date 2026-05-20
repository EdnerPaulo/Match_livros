from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
# AJUSTE DE IMPORTAÇÃO: Apontando para os arquivos corretos da sua estrutura base
from models.database import SessionLocal, Livro, Usuario
from auth import hash_senha, verificar_senha, criar_token
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# --- SCHEMAS (Modelos de Entrada) ---
class UserSchema(BaseModel):
    username: str
    password: str

class LivroSchema(BaseModel):
    titulo: str
    autor: str
    foto_url: Optional[str] = None # <<< MANTIDO: Campo opcional para a foto

# Dependência para o Banco de Dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROTAS DE AUTENTICAÇÃO ---

@router.post("/auth/register", status_code=201)
def register(user: UserSchema, db: Session = Depends(get_db)):
    # <<< MANTIDO: Lógica de cadastro
    db_user = db.query(Usuario).filter(Usuario.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Usuário já existe")
    
    novo_usuario = Usuario(
        username=user.username,
        password_hash=hash_senha(user.password)
    )
    db.add(novo_usuario)
    db.commit()
    return {"message": "Usuário criado com sucesso"}

@router.post("/auth/login")
def login(user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.username == user.username).first()
    if not db_user or not verificar_senha(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    token = criar_token({"sub": db_user.username})
    return {"token": token}

# --- ROTAS DE LIVROS ---

@router.get("/livros")
def listar_livros(db: Session = Depends(get_db)):
    return db.query(Livro).all()

@router.post("/livros")
def criar_livro(livro: LivroSchema, db: Session = Depends(get_db)):
    # <<< MANTIDO: Salva também a foto_url
    novo_livro = Livro(
        titulo=livro.titulo, 
        autor=livro.autor,
        foto_url=livro.foto_url
    )
    db.add(novo_livro)
    db.commit()
    db.refresh(novo_livro)
    return novo_livro

@router.delete("/livros/{livro_id}")
def excluir_livro(livro_id: int, db: Session = Depends(get_db)):
    db_livro = db.query(Livro).filter(Livro.id == livro_id).first()
    if not db_livro:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    db.delete(db_livro)
    db.commit()
    return {"message": "Excluído"}
