import os  # Essencial para segurança
from jose import jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Tenta pegar a chave do Render. Se não achar (local), usa uma chave de teste.
SECRET_KEY = os.getenv("SECRET_KEY", "chave_temporaria_para_testes_locais")
ALGORITHM = "HS256"

# configuração que evita o bug do bcrypt em versões novas do Python
# rsta configuração ignora o erro de 72 bytes e força a compatibilidade
# ignora o erro de compatibilidade do bcrypt
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto", 
    bcrypt__truncate_error=True
)

def hash_senha(senha: str):
    """Cria um hash seguro da senha."""
    return pwd_context.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str):
    """Verifica a senha e protege contra erros de compatibilidade."""
    try:
        return pwd_context.verify(senha_pura, senha_hash)
    except ValueError:
        # Captura o erro 'password cannot be longer than 72 bytes' e outros conflitos
        return False

def criar_token(data: dict):
    """Gera o token JWT para o login."""
    payload = data.copy()
    # Define expiração para 60 minutos
    expira = datetime.utcnow() + timedelta(minutes=60)
    payload.update({"exp": expira})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
