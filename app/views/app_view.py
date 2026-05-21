import streamlit as st
import requests
import os

API_URL = "https://crud-livros-3dg3.onrender.com"

st.set_page_config(page_title="Biblioteca Digital", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None

# --- AUTH ---
with st.sidebar:
    if not st.session_state.token:
        st.header("Login")
        u = st.text_input("Usuário")
        p = st.text_input("Senha", type="password")
        col_btn1, col_btn2 = st.columns(2)
        
        # 🟢 AJUSTE CIRÚRGICO: Associado corretamente à col_btn1
        if col_btn1.button("Entrar"):
            res = requests.post(f"{API_URL}/auth/login", json={"username": u, "password": p})
            if res.status_code == 200:
                st.session_state.token = res.json()["token"]
                st.rerun()
            else: st.error("Erro ao logar")
            
        if col_btn2.button("Cadastrar"):
            res = requests.post(f"{API_URL}/auth/register", json={"username": u, "password": p})
            if res.status_code == 201 or res.status_code == 200:
                st.success("Cadastrado! Faça o login.")
            else: st.error("Erro ao cadastrar")    
    else:
        st.success("Logado")
        if st.button("Sair"):
            st.session_state.token = None
            st.rerun()

# --- INTERFACE CRUD ---
st.title("Gestão de Acervo")

if st.session_state.token:
    # FORMULÁRIO DE CRIAÇÃO
    with st.expander("Novo Registro"):
        c1, c2 = st.columns(2)
        tit = c1.text_input("Título do Livro")
        aut = c2.text_input("Autor")
        f_url = st.text_input("URL da Imagem da Capa (Opcional)")
        if st.button("Salvar Livro"):
            requests.post(f"{API_URL}/livros", json={"titulo": tit, "autor": aut,"foto_url": f_url})
            st.toast("Livro adicionado!")
            st.rerun()

    # LISTAGEM E AÇÕES
    livros = requests.get(f"{API_URL}/livros").json()
    for l in livros:
        with st.container(border=True):
            col_img, col_info, col_del = st.columns([1, 3, 1])
            if l.get('foto_url'):
                col_img.image(l['foto_url'], width=100)
            else:
                col_img.write("📖 No Cover")
            col_info.write(f"**{l['titulo']}** | {l['autor']}")
            if col_del.button("Excluir", key=f"del_{l['id']}"):
                requests.delete(f"{API_URL}/livros/{l['id']}")
                st.rerun()
else:
    st.info("Acesse com seu usuário para gerenciar os livros.")