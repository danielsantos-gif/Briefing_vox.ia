import streamlit as st
import pandas as pd
import random
from supabase import create_client

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Briefing | Vox.ia", page_icon="🟠", layout="wide")

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0f; }
    .stButton>button { width: 100%; border-radius: 8px; }
    .card-pergunta {
        background-color: #1a1a24;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2a2a3a;
        margin-bottom: 10px;
    }
    .status-badge {
        font-size: 0.8rem;
        padding: 2px 8px;
        border-radius: 12px;
        background-color: #331a1a;
        color: #ff9999;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE NAVEGAÇÃO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'acesso_liberado' not in st.session_state: st.session_state.acesso_liberado = False

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- CABEÇALHO ---
col_l, _, col_r = st.columns([1, 2, 1])
with col_l:
    st.image("logos nexus_negativa tagline (2).png", width=150)
with col_r:
    st.image("WhatsApp Image 2026-03-17 at 16.40.54 (1).jpeg", width=120)
st.divider()

# --- LOGIN ---
if not st.session_state.acesso_liberado:
    st.title("🔒 Acesso Restrito")
    senha = st.text_input("Senha de acesso", type="password")
    if st.button("Acessar", type="primary"):
        if senha == "nexus123#":
            st.session_state.acesso_liberado = True
            st.rerun()
        else: st.error("Senha incorreta.")
    st.stop()

# --- PROGRESSO ---
st.progress(st.session_state.step / 5)

# ==========================================
# PASSO 1: CONTEXTO
# ==========================================
if st.session_state.step == 1:
    st.title("1. Identificação e Contexto")
    st.radio("O que estamos analisando?", 
             ["Uma Marca / Empresa", "Um Porta-voz / Executivo", "Uma Narrativa / Tema de Mercado"], 
             key="tipo_analise")
    
    st.text_input("Nome do sujeito principal:", key="empresa", placeholder="Ex: Nestlé, Sustentabilidade")
    
    # Validação de Site Oficial
    site_oficial = st.text_input("Site Oficial (Domínio Principal):", key="site_url", placeholder="https://www.suaempresa.com.br")
    if site_oficial and not ("." in site_oficial):
        st.warning("⚠️ Insira um domínio válido.")

    st.text_area("Descrição detalhada / Objetivo:", key="desc", 
                 placeholder="Descreva o que sua empresa faz e o que espera com esta análise.")
    
    pode_ir = st.session_state.empresa and st.session_state.desc
    st.button("Avançar", on_click=next_step, type="primary", disabled=not pode_ir)

# ==========================================
# PASSO 2: CENÁRIO COMPETITIVO (Mín 5, Máx 10)
# ==========================================
elif st.session_state.step == 2:
    st.title("2. Cenário Competitivo")
    st.markdown("Liste de **5 a 10** principais concorrentes ou temas que disputam sua atenção.")
    
    if 'lista_conc' not in st.session_state:
        st.session_state.lista_conc = [{"nome": "", "site": ""}] * 5 # Começa com 5 campos

    for i, item in enumerate(st.session_state.lista_conc):
        with st.container():
            c1, c2, c3 = st.columns([4, 4, 1])
            item["nome"] = c1.text_input(f"Nome {i+1}", value=item["nome"], key=f"cn_{i}", label_visibility="collapsed", placeholder="Nome")
            
            site_val = c2.text_input(f"Site {i+1}", value=item["site"], key=f"cs_{i}", label_visibility="collapsed", placeholder="site.com.br")
            # Validação de URL
            if site_val and "." not in site_val:
                c2.caption("⚠️ Link inválido")
                item["site"] = ""
            else:
                item["site"] = site_val
                
            if c3.button("🗑️", key=f"del_c_{i}") and len(st.session_state.lista_conc) > 1:
                st.session_state.lista_conc.pop(i)
                st.rerun()

    if len(st.session_state.lista_conc) < 10:
        if st.button("➕ Adicionar Concorrente"):
            st.session_state.lista_conc.append({"nome": "", "site": ""})
            st.rerun()

    validos = [x for x in st.session_state.lista_conc if x["nome"].strip() and x["site"].strip()]
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    btn_ready = len(validos) >= 5
    if st.button("Avançar", on_click=next_step, type="primary", disabled=not btn_ready):
        pass
    if not btn_ready:
        st.error(f"⚠️ Preencha pelo menos 5 concorrentes com sites válidos. (Atual: {len(validos)})")

# ==========================================
# PASSO 3: ATRIBUTOS (Mín 5, Máx 10)
# ==========================================
elif st.session_state.step == 3:
    st.title("3. Atributos da Marca")
    
    col_p, col_n = st.columns(2)
    
    # Lógica igual para Positivos e Negativos
    for label, key_list, col, color in [("Positivos", "lista_pos", col_p, "green"), ("Negativos", "lista_neg", col_n, "red")]:
        with col:
            st.subheader(f"{label}")
            if key_list not in st.session_state: st.session_state[key_list] = [""] * 5
            
            for i, val in enumerate(st.session_state[key_list]):
                c1, c2 = st.columns([8, 2])
                st.session_state[key_list][i] = c1.text_input(f"{label} {i}", value=val, key=f"{key_list}_{i}", label_visibility="collapsed")
                if c2.button("🗑️", key=f"del_{key_list}_{i}") and len(st.session_state[key_list]) > 1:
                    st.session_state[key_list].pop(i)
                    st.rerun()
            
            if len(st.session_state[key_list]) < 10:
                if st.button(f"➕ Add {label}"):
                    st.session_state[key_list].append("")
                    st.rerun()

    st.text_area("Justificativa Estratégica:", key="justificativa", placeholder="Por que esses atributos são vitais?")
    
    p_validos = len([x for x in st.session_state.lista_pos if x.strip()])
    n_validos = len([x for x in st.session_state.lista_neg if x.strip()])
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    ready = p_validos >= 5 and n_validos >= 5 and st.session_state.justificativa
    if st.button("Avançar", on_click=next_step, type="primary", disabled=not ready): pass
    if not ready: st.error("⚠️ Adicione no mínimo 5 atributos em cada categoria.")

# ==========================================
# PASSO 4: PROMPTS (NOVO UX CARDS)
# ==========================================
elif st.session_state.step == 4:
    st.title("4. Inteligência de Busca")
    marca = st.session_state.get("empresa", "Marca")
    
    # ABA A: BRANDED
    st.subheader(f"🔍 Perguntas com '{marca}'")
    if 'lista_b' not in st.session_state: st.session_state.lista_b = []
    
    with st.container(border=True):
        new_b = st.text_input("Nova pergunta Branded (Enter para adicionar):", key="in_b")
        if st.button("Adicionar à Lista Branded") and new_b:
            st.session_state.lista_b.insert(0, new_b)
            st.rerun()
            
    for i, p in enumerate(st.session_state.lista_b):
        with st.container():
            st.markdown(f'<div class="card-pergunta">{p}</div>', unsafe_allow_html=True)
            if marca.lower() not in p.lower():
                st.markdown(f'<span class="status-badge">⚠️ Falta citar "{marca}"</span>', unsafe_allow_html=True)
            if st.button("Remover", key=f"rb_{i}"):
                st.session_state.lista_b.pop(i)
                st.rerun()

    st.divider()
    
    # ABA B: UNBRANDED
    st.subheader("🌐 Perguntas de Mercado (Sem citar nome)")
    if 'lista_u' not in st.session_state: st.session_state.lista_u = []
    
    with st.container(border=True):
        new_u = st.text_input("Nova pergunta de Mercado:", key="in_u")
        if st.button("Adicionar à Lista Mercado") and new_u:
            if marca.lower() in new_u.lower():
                st.error("Não cite a marca nesta lista!")
            else:
                st.session_state.lista_u.insert(0, new_u)
                st.rerun()
                
    for i, p in enumerate(st.session_state.lista_u):
        with st.container():
            st.markdown(f'<div class="card-pergunta">{p}</div>', unsafe_allow_html=True)
            if st.button("Remover", key=f"ru_{i}"):
                st.session_state.lista_u.pop(i)
                st.rerun()

    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    if st.button("Revisar Envio", on_click=next_step, type="primary", disabled=len(st.session_state.lista_b) < 5): pass

# ==========================================
# PASSO 5: ENVIO
# ==========================================
elif st.session_state.step == 5:
    st.title("5. Revisão e Envio")
    st.write(f"**Sujeito:** {st.session_state.empresa}")
    st.write(f"**Prompts:** {len(st.session_state.lista_b)} Branded / {len(st.session_state.lista_u)} Mercado")
    
    st.checkbox("Aceito os termos de tratamento de dados (LGPD).", key="lgpd")
    
    if st.button("🚀 FINALIZAR BRIEFING", type="primary", disabled=not st.session_state.lgpd):
        # Lógica de insert no Supabase aqui
        st.success("Briefing enviado com sucesso! Nossa equipe entrará em contato.")
        st.balloons()
