from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import SessionLocal, Livro, Usuario
from app.controllers.auth import criar_token, verificar_senha, hash_senha

router = APIRouter()

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# AUTH ROUTES
@router.post("/auth/register")
def register(dados: dict, db: Session = Depends(get_db)):
    novo_user = Usuario(username=dados['username'], password_hash=hash_senha(dados['password']))
    db.add(novo_user)
    db.commit()
    return {"status": "sucesso"}

@router.post("/auth/login")
def login(dados: dict, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == dados['username']).first()
    if not user or not verificar_senha(dados['password'], user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"token": criar_token({"sub": user.username})}

# CRUD LIVROS
@router.get("/livros")
def listar_livros(db: Session = Depends(get_db)):
    # <<< AJUSTE SEGURO: Mapeia os dados explicitamente para evitar erros de serialização no Render
    livros_db = db.query(Livro).all()
    resultado = []
    for l in livros_db:
        resultado.append({
            "id": l.id,
            "titulo": l.titulo,
            "autor": l.autor,
            "foto_url": getattr(l, 'foto_url', None) or ""  # Se for nulo ou não existir, devolve texto vazio
        })
    return resultado

@router.post("/livros")
def criar_livro(livro: dict, db: Session = Depends(get_db)):
    # <<< AJUSTE CIRÚRGICO: Cria garantindo que a foto_url vá limpa se não for enviada
    novo = Livro(
        titulo=livro['titulo'], 
        autor=livro['autor'],
        foto_url=livro.get('foto_url', '')  # Evita salvar como nulo puro que quebra consultas antigas
    )
    db.add(novo)
    db.commit()
    return {"status": "criado"}

@router.put("/livros/{id}")
def editar_livro(id: int, dados: dict, db: Session = Depends(get_db)):
    livro = db.query(Livro).filter(Livro.id == id).first()
    if not livro: raise HTTPException(status_code=404)
    livro.titulo = dados['titulo']
    livro.autor = dados['autor']
    if 'foto_url' in dados:
        livro.foto_url = dados['foto_url']
    db.commit()
    return {"status": "atualizado"}

@router.delete("/livros/{id}")
def excluir_livro(id: int, db: Session = Depends(get_db)):
    livro = db.query(Livro).filter(Livro.id == id).first()
    if not livro: raise HTTPException(status_code=404)
    db.delete(livro)
    db.commit()
    return {"status": "removido"}
