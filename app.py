import streamlit as st
import pandas as pd
import random
import uuid
from supabase import create_client, Client

# --- CONFIGURAÇÃO INICIAL ---
# Define o layout largo e o título da aba do navegador 
st.set_page_config(page_title="Briefing | Vox.ia", page_icon="🟠", layout="wide")

# --- CONEXÃO COM SUPABASE ---
# Utiliza st.secrets para segurança (LGPD) 
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("⚠️ Erro de conexão: Verifique as chaves no Secrets do Streamlit.")
        st.stop()

supabase = init_connection()

# --- INICIALIZAÇÃO DO ESTADO (SESSION STATE) ---
# Garante que o sistema não "esqueça" os dados entre as páginas
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'acesso_liberado' not in st.session_state:
    st.session_state.acesso_liberado = False
if 'tipo_usuario' not in st.session_state:
    st.session_state.tipo_usuario = None

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- CABEÇALHO COM LOGOS ---
# Busca as imagens na raiz do GitHub conforme sua organização
col_l, col_m, col_r = st.columns([1, 2, 1])
with col_l:
    try: st.image("logos nexus_negativa tagline (2).png", width=150)
    except: st.caption("[Logo Nexus]")
with col_r:
    try: st.image("WhatsApp Image 2026-03-17 at 16.40.54 (1).jpeg", width=120) 
    except: st.caption("[Logo Vox.ia]")
st.divider()

# ==========================================
# 1. MÓDULO DE ERRATA (VIA URL)
# ==========================================
if "errata" in st.query_params:
    id_prot = st.query_params["errata"]
    st.title("📝 Correção de Briefing")
    
    # Busca dados reais do banco para sobreposição [cite: 3, 57]
    res = supabase.table("briefings").select("*").eq("protocolo", id_prot).execute()
    if not res.data:
        st.error("Protocolo não encontrado.")
        st.stop()
    
    dados = res.data[0]
    st.warning(f"Ajuste os prompts para: {dados['nome_sujeito']}. O novo envio substituirá o antigo[cite: 5].")
    
    branded_ed = st.data_editor(pd.DataFrame(dados['prompts_branded']), use_container_width=True, num_rows="dynamic", key="err_b")
    unbranded_ed = st.data_editor(pd.DataFrame(dados['prompts_unbranded']), use_container_width=True, num_rows="dynamic", key="err_u")
    
    if st.button("Salvar e Reenviar", type="primary"):
        supabase.table("briefings").update({
            "prompts_branded": branded_ed.to_dict('records'),
            "prompts_unbranded": unbranded_ed.to_dict('records'),
            "status": "Corrigido"
        }).eq("protocolo", id_prot).execute()
        st.success("Briefing atualizado!")
        st.balloons()
    st.stop()

# ==========================================
# 2. SISTEMA DE LOGIN (CLIENTE VS ADMIN)
# ==========================================
if not st.session_state.acesso_liberado:
    st.title("🔒 Portal de Acesso Vox.ia")
    t1, t2 = st.tabs(["Acesso Cliente", "Acesso Equipe (Admin)"])
    
    with t1:
        senha_cli = st.text_input("Senha do Projeto", type="password", key="s_cli")
        if st.button("Entrar como Cliente"):
            if senha_cli == "nexus123#":
                st.session_state.acesso_liberado = True
                st.session_state.tipo_usuario = "cliente"
                st.rerun()
            else: st.error("Senha inválida.")
            
    with t2:
        st.info("Acesso via código OTP (Simulação: 123456)")
        user_admin = st.text_input("E-mail corporativo", key="adm_mail")
        otp_adm = st.text_input("Código de 6 dígitos", type="password")
        if st.button("Validar Admin"):
            if otp_adm == "123456":
                st.session_state.acesso_liberado = True
                st.session_state.tipo_usuario = "admin"
                st.rerun()
    st.stop()

# ==========================================
# 3. PAINEL ADMIN (DASHBOARD)
# ==========================================
if st.session_state.tipo_usuario == "admin":
    st.title("⚙️ Dashboard Estratégico")
    tab_g, tab_m = st.tabs(["Gestão de Dados", "Análise Macro"])
    
    with tab_g:
        res_adm = supabase.table("briefings").select("protocolo, data_envio, nome_sujeito, status").order("id", desc=True).execute()
        if res_adm.data:
            st.dataframe(pd.DataFrame(res_adm.data), use_container_width=True)
            st.text_input("Gerar Link de Errata para Protocolo:", key="gen_err")
            if st.session_state.gen_err:
                st.code(f"https://{st.secrets.get('APP_URL', 'seu-site')}.app/?errata={st.session_state.gen_err}")
    
    with tab_m:
        st.subheader("Indicadores-Chave [cite: 4]")
        c1, c2 = st.columns(2)
        c1.metric("Total de Briefings", len(res_adm.data))
        c2.metric("Taxa de Errata", "15%")
        st.bar_chart(pd.DataFrame({"Volume": [10, 20, 15]}, index=["Marca", "Porta-voz", "Narrativa"]))
    
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# ==========================================
# 4. FLUXO DO CLIENTE (WIZARD)
# ==========================================
st.progress(st.session_state.step / 5)

if st.session_state.step == 1:
    st.title("1. Contexto da Marca [cite: 6]")
    # Define o fluxo que será lembrado nos passos seguintes [cite: 48, 49]
    st.radio("O que analisaremos?", 
             ["Uma Marca / Empresa", "Um Porta-voz / Executivo", "Uma Narrativa / Tema de Mercado"], 
             key="tipo_analise")
    st.text_input("Nome do sujeito principal:", key="empresa", placeholder="Ex: Nestlé, Sustentabilidade [cite: 49]")
    st.text_area("Descrição detalhada:", key="desc", placeholder="O que sua empresa faz? [cite: 7, 51]")
    st.button("Avançar", on_click=next_step, type="primary")

elif st.session_state.step == 2:
    st.title("2. Cenário Competitivo [cite: 76, 77]")
    tipo = st.session_state.get("tipo_analise", "Uma Marca / Empresa")
    
    # Layout aprimorado com colunas físicas [cite: 89, 90]
    with st.container(border=True):
        if "lista_conc" not in st.session_state: st.session_state.lista_conc = [{"nome": "", "site": ""}]
        
        for i, item in enumerate(st.session_state.lista_conc):
            c1, c2, c3 = st.columns([4, 4, 1])
            item["nome"] = c1.text_input(f"Nome {i}", value=item["nome"], key=f"cn_{i}", label_visibility="collapsed", placeholder="Concorrente")
            if tipo != "Uma Narrativa / Tema de Mercado":
                item["site"] = c2.text_input(f"Site {i}", value=item["site"], key=f"cs_{i}", label_visibility="collapsed", placeholder="https://...")
            if c3.button("🗑️", key=f"del_{i}") and len(st.session_state.lista_conc) > 1:
                st.session_state.lista_conc.pop(i)
                st.rerun()
        
        if st.button("➕ Adicionar"):
            st.session_state.lista_conc.append({"nome": "", "site": ""})
            st.rerun()

    col_l, col_r = st.columns([1, 5])
    col_l.button("Voltar", on_click=prev_step)
    col_r.button("Avançar", on_click=next_step, type="primary")

elif st.session_state.step == 3:
    st.title("3. Atributos e Valores [cite: 32, 198]")
    c1, c2 = st.columns(2)
    with c1: st.text_area("✅ Positivos (1 por linha):", key="pos", help="Ex: Inovador, Confiável [cite: 35, 200]")
    with c2: st.text_area("❌ Negativos (1 por linha):", key="neg", help="Ex: Lento, Caro [cite: 236]")
    st.text_input("Justificativa estratégica:", key="just", placeholder="Por que esses atributos? [cite: 228]")
    
    col_l, col_r = st.columns([1, 5])
    col_l.button("Voltar", on_click=prev_step)
    col_r.button("Avançar", on_click=next_step, type="primary")

elif st.session_state.step == 4:
    st.title("4. Inteligência de Busca [cite: 249, 610]")
    marca = st.session_state.get("empresa", "").lower()
    
    st.subheader("A. Branded (Com sua marca) [cite: 249]")
    # Tabela interativa para visualização do que já foi adicionado [cite: 254, 255]
    if "df_b" not in st.session_state: st.session_state.df_b = pd.DataFrame([{"Pergunta": ""}])
    st.session_state.df_b = st.data_editor(st.session_state.df_b, num_rows="dynamic", use_container_width=True, hide_index=True)
    
    # Alerta vermelho suave se esquecer a marca 
    for p in st.session_state.df_b["Pergunta"]:
        if p and marca not in p.lower():
            st.markdown(f'<div style="color: #ff4d4d; background: #331a1a; padding: 10px; border-radius: 5px;">💡 Sugestão: A pergunta "{p}" deve citar "{marca.title()}".</div>', unsafe_allow_html=True)

    st.subheader("B. Unbranded (Mercado - Sem citar marca) [cite: 610, 614]")
    if "df_u" not in st.session_state: st.session_state.df_u = pd.DataFrame([{"Pergunta": ""}])
    st.session_state.df_u = st.data_editor(st.session_state.df_u, num_rows="dynamic", use_container_width=True, hide_index=True)
    
    col_l, col_r = st.columns([1, 5])
    col_l.button("Voltar", on_click=prev_step)
    col_r.button("Revisar e Enviar", on_click=next_step, type="primary")

elif st.session_state.step == 5:
    st.title("5. Revisão Final [cite: 971]")
    st.checkbox("Concordo com o tratamento dos dados (LGPD).", key="lgpd")
    
    if st.button("🚀 Enviar para Diagnóstico", type="primary", disabled=not st.session_state.get("lgpd")):
        prot = f"BX-{random.randint(1000, 9999)}"
        # Envio estruturado para o Supabase [cite: 3, 5, 44]
        supabase.table("briefings").insert({
            "protocolo": prot,
            "nome_sujeito": st.session_state.get("empresa"),
            "tipo_analise": st.session_state.get("tipo_analise"),
            "concorrentes": st.session_state.lista_conc,
            "prompts_branded": st.session_state.df_b.to_dict('records'),
            "prompts_unbranded": st.session_state.df_u.to_dict('records'),
            "status": "Novo"
        }).execute()
        st.success(f"Enviado! Protocolo: {prot}")
        st.balloons()
