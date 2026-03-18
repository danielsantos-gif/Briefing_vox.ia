import streamlit as st
import pandas as pd
import random
import base64
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit.components.v1 as components
import textwrap
from supabase import create_client

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="Briefing | Vox.ia",
    page_icon="🎯",
    layout="wide"
)

# --- CONEXÃO COM SUPABASE ---
@st.cache_resource
def init_connection():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("⚠️ As chaves do Supabase não foram encontradas no Secrets do Streamlit.")
        st.stop()

supabase = init_connection()

# --- FUNÇÃO OTIMIZADA PARA IMAGEM DE FUNDO ---
@st.cache_data
def get_base64_image(file_name):
    try:
        with open(file_name, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

# --- ENVIO DE E-MAIL VIA SMTP ---
def enviar_email_lembrete(destinatario: str, nome_projeto: str, data_apresentacao: str):
    """
    Envia um e-mail de lembrete via SMTP simples.
    Requer no st.secrets:
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_FROM
    """
    try:
        host  = st.secrets["SMTP_HOST"]
        port  = int(st.secrets.get("SMTP_PORT", 587))
        user  = st.secrets["SMTP_USER"]
        pwd   = st.secrets["SMTP_PASS"]
        from_ = st.secrets.get("SMTP_FROM", user)
    except KeyError as e:
        st.error(f"⚠️ Configuração de e-mail ausente no Secrets: {e}")
        return False

    assunto = f"[Vox.ia] Lembrete: entrega de '{nome_projeto}' em 2 dias"
    corpo_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 560px; margin: auto;">
        <h2 style="color: #F58220;">📅 Lembrete de Entrega — Vox.ia</h2>
        <p>Olá,</p>
        <p>Este é um aviso automático: a apresentação do projeto <strong>{nome_projeto}</strong>
        está agendada para <strong>{data_apresentacao}</strong>, ou seja, em <strong>2 dias</strong>.</p>
        <p>Certifique-se de que o diagnóstico está finalizado e o relatório preparado.</p>
        <hr style="border-color: #333;">
        <p style="color: #888; font-size: 12px;">Mensagem automática gerada pelo sistema Briefing Vox.ia — Nexus.</p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = assunto
    msg["From"]    = from_
    msg["To"]      = destinatario
    msg.attach(MIMEText(corpo_html, "html"))

    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(user, pwd)
            smtp.sendmail(from_, destinatario, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail para {destinatario}: {e}")
        return False

# --- ESTILIZAÇÃO CUSTOMIZADA ---
st.markdown("""
    <style>
    .stApp { background-color: #0a0a0f; }

    div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div {
        background-color: #121218 !important;
        border: 1px solid #3a3a4a !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
        border: 1px solid #F58220 !important;
        box-shadow: 0 0 8px rgba(245, 130, 32, 0.4) !important;
    }

    .card-pergunta {
        background-color: #1a1a24;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #2a2a3a;
        margin-bottom: 8px;
    }
    .card-pergunta-marcada {
        background-color: #2a1a0a;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid #F58220;
        margin-bottom: 8px;
    }

    .stButton > button {
        border-radius: 8px !important;
        height: 48px !important;
        padding: 8px 16px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        border: 1px solid #3a3a4a !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #F58220 !important;
        color: #050508 !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #ff9d47 !important;
        transform: translateY(-2px);
    }

    [data-testid="stSidebar"] {
        background-color: #0d0d14;
        border-right: 1px solid #2a2a3a;
    }
    .sidebar-step {
        padding: 16px 12px;
        margin-bottom: 8px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        font-size: 15px;
        transition: all 0.3s ease;
    }
    .sidebar-step.completed { color: #ffffff; }
    .sidebar-step.current {
        background-color: #2a2a3a;
        color: #ffffff;
        font-weight: bold;
        border-left: 4px solid #F58220;
    }
    .sidebar-step.pending { color: #666666; }

    .circle-check {
        position: relative;
        min-width: 24px; height: 24px; border: 2px solid #4CAF50; border-radius: 50%;
        display: flex; justify-content: center; align-items: center;
        color: #4CAF50; margin-right: 12px; font-weight: bold; font-size: 14px;
        animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .circle-check::after {
        content: '';
        position: absolute;
        top: 50%; left: 50%;
        width: 4px; height: 4px;
        border-radius: 50%;
        opacity: 0;
        box-shadow:
            12px -12px 0 0 #F58220,
            -12px -12px 0 0 #4CAF50,
            12px 12px 0 0 #ffffff,
            -12px 12px 0 0 #F58220,
            0px -18px 0 0 #4CAF50,
            0px 18px 0 0 #ffffff,
            18px 0px 0 0 #F58220,
            -18px 0px 0 0 #4CAF50;
        animation: spark 0.6s ease-out forwards;
        animation-delay: 0.15s;
    }
    .circle-dotted {
        min-width: 24px; height: 24px; border: 2px dotted #F58220; border-radius: 50%;
        display: flex; justify-content: center; align-items: center; margin-right: 12px;
    }
    .circle-empty {
        min-width: 24px; height: 24px; border: 2px solid #444; border-radius: 50%;
        display: flex; justify-content: center; align-items: center; margin-right: 12px;
    }

    @keyframes popIn {
        0% { transform: scale(0); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes spark {
        0% { transform: translate(-50%, -50%) scale(0.3); opacity: 1; }
        100% { transform: translate(-50%, -50%) scale(1.6); opacity: 0; }
    }

    .success-checkmark { width: 120px; height: 120px; margin: 0 auto; display: block; }
    .checkmark_circle { stroke-dasharray: 166; stroke-dashoffset: 166; stroke-width: 4; stroke-miterlimit: 10; stroke: #4CAF50; fill: none; animation: stroke 0.6s cubic-bezier(0.65, 0, 0.45, 1) forwards; }
    .checkmark_check { transform-origin: 50% 50%; stroke-dasharray: 48; stroke-dashoffset: 48; stroke-width: 4; stroke-linecap: round; stroke: #4CAF50; fill: none; animation: stroke 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.6s forwards; }
    @keyframes stroke { 100% { stroke-dashoffset: 0; } }
    </style>
""", unsafe_allow_html=True)

# --- CONTROLE DE NAVEGAÇÃO E COFRE DE MEMÓRIA ---
if 'intro_viewed' not in st.session_state: st.session_state.intro_viewed = False

if 'dados' not in st.session_state:
    st.session_state.dados = {
        'empresa': '', 'tipo_analise': 'Uma Marca / Empresa', 'site_url': '',
        'desc_pilar': '', 'objetivos': [], 'justificativa': '', 'nuances': '', 'email': ''
    }

if 'step' not in st.session_state: st.session_state.step = 1
if 'acesso_liberado' not in st.session_state: st.session_state.acesso_liberado = False
if 'tipo_usuario' not in st.session_state: st.session_state.tipo_usuario = None

if 'lista_b' not in st.session_state: st.session_state.lista_b = []
if 'lista_u' not in st.session_state: st.session_state.lista_u = []
if 'lista_conc' not in st.session_state: st.session_state.lista_conc = [{"nome": "", "site": ""} for _ in range(5)]
if 'lista_pos' not in st.session_state: st.session_state.lista_pos = [""] * 5
if 'lista_neg' not in st.session_state: st.session_state.lista_neg = [""] * 5

if 'limpar_b' not in st.session_state: st.session_state.limpar_b = False
if 'limpar_u' not in st.session_state: st.session_state.limpar_u = False

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1


# ==========================================
# MÓDULO DE ERRATA (VIA URL) — CORRIGIDO
# ==========================================
if "errata" in st.query_params:
    id_prot = st.query_params["errata"]

    res = supabase.table("briefings").select("*").eq("protocolo", id_prot).execute()
    if not res.data:
        st.error("Erro: Protocolo não encontrado.")
        st.stop()

    dados_banco = res.data[0]
    nome_proj   = dados_banco.get("nome_sujeito", id_prot)

    # Perguntas marcadas para revisão pelo admin
    marcadas_b = set(dados_banco.get("errata_marcadas_branded",   []))  # índices como strings
    marcadas_u = set(dados_banco.get("errata_marcadas_unbranded", []))

    lista_b_banco = dados_banco.get("prompts_branded",   []) or []
    lista_u_banco = dados_banco.get("prompts_unbranded", []) or []

    # Filtra apenas as perguntas marcadas
    pergs_b = [(i, p) for i, p in enumerate(lista_b_banco) if str(i) in marcadas_b]
    pergs_u = [(i, p) for i, p in enumerate(lista_u_banco) if str(i) in marcadas_u]

    st.title(f"📝 Revisão de Briefing — {nome_proj}")

    if not pergs_b and not pergs_u:
        st.info("Nenhuma pergunta foi marcada para revisão. Entre em contato com a equipe Nexus.")
        st.stop()

    st.warning("Ajuste apenas as perguntas destacadas abaixo. As demais permanecem inalteradas.")

    novos_b = list(lista_b_banco)  # cópia completa para preservar não-marcadas
    novos_u = list(lista_u_banco)

    if pergs_b:
        st.subheader("🔵 Perguntas Institucionais (Branded) para revisar")
        for idx, p in pergs_b:
            novo_texto = st.text_area(
                f"Pergunta {idx + 1}:",
                value=p.get("Pergunta", ""),
                key=f"errata_b_{idx}"
            )
            novos_b[idx] = {"Pergunta": novo_texto}

    if pergs_u:
        st.subheader("🟠 Perguntas de Mercado (Non Branded) para revisar")
        for idx, p in pergs_u:
            novo_texto = st.text_area(
                f"Pergunta {idx + 1}:",
                value=p.get("Pergunta", ""),
                key=f"errata_u_{idx}"
            )
            novos_u[idx] = {"Pergunta": novo_texto}

    st.divider()
    if st.button("✅ Enviar Revisão", type="primary"):
        supabase.table("briefings").update({
            "prompts_branded":          novos_b,
            "prompts_unbranded":        novos_u,
            "errata_marcadas_branded":  [],   # limpa marcações após envio
            "errata_marcadas_unbranded": [],
            "status": "Em ajuste"
        }).eq("protocolo", id_prot).execute()
        st.success("✅ Revisão enviada com sucesso! A equipe Nexus foi notificada.")
    st.stop()


# ==========================================
# 0. TELA DE INTRODUÇÃO (SPLASH SCREEN)
# ==========================================
if not st.session_state.intro_viewed:
    st.markdown("""
<style>
.stApp { background: transparent !important; }
.block-container { padding-top: 1rem !important; }
header { display: none !important; }
.stButton > button { height: 64px !important; font-size: 20px !important; border-radius: 12px !important; font-weight: bold !important; }
.splash-bg { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at center, #1a0a00 0%, #050508 100%); z-index: -1; overflow: hidden; }
.orb { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.6; animation: moveOrbs 15s infinite alternate ease-in-out; }
.orb-1 { width: 45vw; height: 45vw; background: #F58220; top: -15%; left: -10%; animation-duration: 20s; }
.orb-2 { width: 35vw; height: 35vw; background: #ff9d47; bottom: -10%; right: -5%; animation-direction: alternate-reverse; }
@keyframes moveOrbs { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(15vw, 15vh) scale(1.2); } }
</style>
<div class="splash-bg"><div class="orb orb-1"></div><div class="orb orb-2"></div></div>
""", unsafe_allow_html=True)

    img_nexus = get_base64_image("logos nexus_negativa tagline (2).png")
    img_voxia = get_base64_image("VOXIA - Logo negativo branco.png")

    st.markdown(f"""
<div style="display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; margin-top: 16vh;">
    <div style="display: flex; flex-direction: row; justify-content: center; align-items: center; gap: 40px; margin-bottom: 25px;">
        <img src="data:image/png;base64,{img_nexus}" width="160">
        <img src="data:image/png;base64,{img_voxia}" width="120">
    </div>
    <h1 style="color: #F58220; font-size: 4.5rem; margin-bottom: 0; font-weight: 900;">Briefing para vox.ia</h1>
    <h2 style="font-size: 2.8rem; margin-top: 8px; color: #fff; font-weight: 700;">Reputação e Presença de Marca<br>na Inteligência Artificial.</h2>
    <p style="font-size: 1.2rem; color: #ccc; max-width: 750px; margin: 24px auto 35px auto; line-height: 1.6;">
        Este diagnóstico mapeia a presença da sua marca no ecossistema de IA Generativa. A precisão dos dados a seguir é fundamental para treinarmos nossos modelos de análise e garantir um relatório fiel à sua realidade.
    </p>
</div>
""", unsafe_allow_html=True)

    _, col_btn, _ = st.columns([2.5, 3, 2.5])
    with col_btn:
        if st.button("Vamos começar", type="primary", use_container_width=True):
            st.session_state.intro_viewed = True
            st.rerun()
    st.stop()


# ==========================================
# 1. LOGIN
# ==========================================
if not st.session_state.acesso_liberado:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>Portal de Acesso</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #888;'>Selecione seu perfil para continuar</p>", unsafe_allow_html=True)
            st.divider()
            t1, t2 = st.tabs(["Sou Cliente", "Equipe Nexus"])
            with t1:
                st.markdown("<br>", unsafe_allow_html=True)
                senha_cli = st.text_input("Senha do Projeto", type="password", key="s_cli", placeholder="Insira a senha fornecida...")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Entrar no Briefing →", type="primary"):
                    if senha_cli == "nexus123#":
                        st.session_state.acesso_liberado = True
                        st.session_state.tipo_usuario = "cliente"
                        st.rerun()
                    else: st.error("Aviso: Senha inválida.")
            with t2:
                st.info("Acesso via código OTP (Simulação: 123456)")
                user_admin = st.text_input("E-mail corporativo", key="adm_mail", placeholder="nome@nexus.com")
                otp_adm   = st.text_input("Código de 6 dígitos", type="password")
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Acessar Painel Admin →", type="primary"):
                    if otp_adm == "123456":
                        st.session_state.acesso_liberado = True
                        st.session_state.tipo_usuario = "admin"
                        st.rerun()
                    else: st.error("Aviso: Código inválido.")
    st.stop()


# ==========================================
# PAINEL ADMIN
# ==========================================
if st.session_state.tipo_usuario == "admin":
    c_title, c_btn = st.columns([8, 2])
    with c_title:
        st.title("⚙️ Dashboard Estratégico")
    with c_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 Sair do Painel", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("Gestão centralizada de briefings, status de clientes e agendamentos.")
    st.divider()

    tab_g, tab_m = st.tabs(["📊 Gestão de Status e Tabela", "🔎 Inspeção, Errata e Download"])

    # ----------------------------------------------------------
    # TAB 1 — GESTÃO DE STATUS
    # ----------------------------------------------------------
    with tab_g:
        res_adm = supabase.table("briefings").select("*").order("id", desc=True).execute()

        if res_adm.data:
            df_admin = pd.DataFrame(res_adm.data)

            for col in ['responsavel', 'data_apresentacao', 'link_apresentacao']:
                if col not in df_admin.columns:
                    df_admin[col] = ""

            df_display = df_admin[[
                'id', 'data_envio', 'protocolo', 'nome_sujeito',
                'status', 'responsavel', 'data_apresentacao', 'link_apresentacao'
            ]].copy()

            try:
                df_display['data_envio'] = pd.to_datetime(df_display['data_envio']).dt.strftime('%d/%m/%Y')
            except:
                pass

            with st.container(border=True):
                st.subheader("📋 Visão Geral dos Briefings")
                st.caption("Acompanhe o andamento de todos os protocolos gerados pelos clientes.")
                st.dataframe(
                    df_display,
                    column_config={
                        "id": None,
                        "data_envio":         st.column_config.TextColumn("Data",          width="small"),
                        "protocolo":          st.column_config.TextColumn("Protocolo",     width="small"),
                        "nome_sujeito":       st.column_config.TextColumn("Cliente",       width="medium"),
                        "status":             st.column_config.TextColumn("Status",        width="medium"),
                        "responsavel":        st.column_config.TextColumn("Responsável",   width="small"),
                        "data_apresentacao":  st.column_config.TextColumn("Agendamento",   width="small"),
                        "link_apresentacao":  st.column_config.LinkColumn("Apresentação",  width="medium"),
                    },
                    use_container_width=True,
                    hide_index=True
                )

            st.markdown("<br>", unsafe_allow_html=True)

            col_edit, col_email = st.columns(2)

            # --- Edição de status / agendamento / link / responsável ---
            with col_edit:
                with st.container(border=True):
                    st.markdown("**✏️ Atualizar Status, Agendamento e Apresentação**")
                    st.caption("Selecione um cliente para editar suas informações.")

                    opcoes_proj = [""] + list(
                        df_admin['protocolo'].astype(str) + " - " + df_admin['nome_sujeito'].astype(str)
                    )
                    proj_selecionado = st.selectbox("Selecione o Projeto:", opcoes_proj)

                    if proj_selecionado:
                        prot_selec   = proj_selecionado.split(" - ")[0]
                        dados_proj   = df_admin[df_admin['protocolo'] == prot_selec].iloc[0]

                        status_atual  = dados_proj.get('status', 'Novo')
                        resp_atual    = dados_proj.get('responsavel', '')
                        data_atual_str= dados_proj.get('data_apresentacao', '')
                        link_atual    = dados_proj.get('link_apresentacao', '')

                        lista_status = [
                            "Novo", "Briefing aprovado", "Cadastro na plataforma feito",
                            "Em produção", "Produção finalizada", "Apresentação agendada",
                            "Concluído", "Em ajuste"
                        ]
                        idx_status = lista_status.index(status_atual) if status_atual in lista_status else 0

                        novo_status = st.selectbox("Atualizar Progresso:", lista_status, index=idx_status)

                        data_obj = None
                        if pd.notna(data_atual_str) and str(data_atual_str).strip():
                            try:
                                data_obj = datetime.datetime.strptime(data_atual_str, "%d/%m/%Y").date()
                            except: pass

                        c1, c2 = st.columns(2)
                        novo_resp  = c1.text_input("Responsável:", value=resp_atual if pd.notna(resp_atual) else "")
                        nova_data  = c2.date_input("Agendamento:", value=data_obj, format="DD/MM/YYYY")

                        # ★ NOVO: campo link da apresentação
                        novo_link = st.text_input(
                            "🔗 Link da Apresentação:",
                            value=link_atual if pd.notna(link_atual) else "",
                            placeholder="https://drive.google.com/..."
                        )

                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
                            nova_data_str = nova_data.strftime("%d/%m/%Y") if nova_data else ""
                            with st.spinner("Salvando no Supabase..."):
                                try:
                                    supabase.table("briefings").update({
                                        "status":             novo_status,
                                        "responsavel":        novo_resp,
                                        "data_apresentacao":  nova_data_str,
                                        "link_apresentacao":  novo_link,   # ★ salva o link
                                    }).eq("protocolo", prot_selec).execute()
                                    st.success("✅ Briefing atualizado com sucesso!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Erro ao salvar: {e}")

            # --- ★ NOVO: Lembretes por e-mail ---
            with col_email:
                with st.container(border=True):
                    st.markdown("**📧 Lembretes Automáticos por E-mail**")
                    st.caption(
                        "Clique abaixo para verificar quais projetos têm apresentação em **2 dias** "
                        "e disparar o aviso ao responsável cadastrado."
                    )

                    hoje      = datetime.date.today()
                    alvo_data = hoje + datetime.timedelta(days=2)

                    candidatos = []
                    for _, row in df_admin.iterrows():
                        d_str = row.get("data_apresentacao", "")
                        resp  = row.get("responsavel", "")
                        if not d_str or not resp:
                            continue
                        try:
                            d = datetime.datetime.strptime(str(d_str), "%d/%m/%Y").date()
                            if d == alvo_data:
                                candidatos.append(row)
                        except:
                            pass

                    if candidatos:
                        st.warning(f"⚠️ {len(candidatos)} projeto(s) com apresentação em 2 dias:")
                        for row in candidatos:
                            st.write(f"• **{row['nome_sujeito']}** → {row['responsavel']} ({row['data_apresentacao']})")

                        if st.button("📤 Disparar Lembretes Agora", type="primary", use_container_width=True):
                            enviados = 0
                            for row in candidatos:
                                ok = enviar_email_lembrete(
                                    destinatario      = row['responsavel'],
                                    nome_projeto      = row['nome_sujeito'],
                                    data_apresentacao = row['data_apresentacao']
                                )
                                if ok:
                                    enviados += 1
                            st.success(f"✅ {enviados}/{len(candidatos)} e-mail(s) enviado(s).")
                    else:
                        st.info(f"Nenhuma apresentação agendada para {alvo_data.strftime('%d/%m/%Y')}.")
                        st.button("📤 Disparar Lembretes Agora", disabled=True, use_container_width=True)

        else:
            st.info("Nenhum briefing recebido ainda.")

    # ----------------------------------------------------------
    # TAB 2 — INSPEÇÃO, ERRATA E DOWNLOAD
    # ----------------------------------------------------------
    with tab_m:
        st.subheader("Inspeção Profunda, Errata e Download")

        if res_adm.data:
            opcoes_dropdown = [""] + [
                f"{row['nome_sujeito']} (Prot: {row['protocolo']})"
                for _, row in df_admin.iterrows()
            ]
            selecao = st.selectbox("Selecione um cliente:", opcoes_dropdown)

            if selecao:
                prot_selecionado = selecao.split(" (Prot: ")[-1].replace(")", "")
                dados_prot       = df_admin[df_admin['protocolo'] == prot_selecionado].iloc[0]

                # Listas com fallback seguro
                lista_b    = dados_prot.get('prompts_branded')   or []
                lista_u    = dados_prot.get('prompts_unbranded') or []
                lista_conc = dados_prot.get('concorrentes')      or []
                lista_pos  = dados_prot.get('atributos_pos')     or []
                lista_neg  = dados_prot.get('atributos_neg')     or []

                # Marcações existentes
                marc_b_atual = set(dados_prot.get("errata_marcadas_branded",   []) or [])
                marc_u_atual = set(dados_prot.get("errata_marcadas_unbranded", []) or [])

                c_grafico, c_doc = st.columns([1.5, 1])

                with c_grafico:
                    st.markdown(f"**Volume de Prompts: {dados_prot['nome_sujeito']}**")
                    st.bar_chart(pd.DataFrame(
                        {"Qtd": [len(lista_b), len(lista_u)]},
                        index=["Branded", "Non Branded"]
                    ))

                with c_doc:
                    st.markdown("**Exportação Rápida**")
                    texto_doc = f"""DIAGNÓSTICO VOX.IA - BRIEFING COMPLETO
==================================================
Sujeito Analisado: {dados_prot['nome_sujeito']}
Protocolo: {dados_prot['protocolo']}
Tipo: {dados_prot['tipo_analise']}
Status: {dados_prot['status']}
Responsável: {dados_prot.get('responsavel', 'Não atribuído')}
Apresentação: {dados_prot.get('data_apresentacao', 'Não agendada')}
Link Apresentação: {dados_prot.get('link_apresentacao', 'Não informado')}

CONTEXTO E OBJETIVOS:
--------------------------------------------------
{dados_prot.get('descricao', '')}

CENÁRIO COMPETITIVO:
--------------------------------------------------\n"""
                    for c in lista_conc:
                        texto_doc += f"- {c.get('nome', '')} ({c.get('site', '')})\n"
                    texto_doc += "\nATRIBUTOS DA MARCA:\n--------------------------------------------------\n"
                    texto_doc += "Positivos:\n" + "".join(f"- {p}\n" for p in lista_pos)
                    texto_doc += "\nNegativos:\n" + "".join(f"- {n}\n" for n in lista_neg)
                    texto_doc += f"\nJustificativa:\n{dados_prot.get('contexto_atributos', '')}\n"
                    texto_doc += "\nPROMPTS BRANDED:\n--------------------------------------------------\n"
                    for p in lista_b: texto_doc += f"- {p.get('Pergunta', '')}\n"
                    texto_doc += "\nPROMPTS NON BRANDED:\n--------------------------------------------------\n"
                    for p in lista_u: texto_doc += f"- {p.get('Pergunta', '')}\n"

                    st.download_button(
                        "📄 Baixar Briefing (.txt)",
                        data=texto_doc,
                        file_name=f"{dados_prot['nome_sujeito']}_briefing.txt",
                        mime="text/plain",
                        type="primary",
                        use_container_width=True
                    )

                    # Link de apresentação
                    link_ap = dados_prot.get("link_apresentacao", "")
                    if link_ap:
                        st.markdown(f"[🎞️ Abrir Apresentação]({link_ap})", unsafe_allow_html=False)

                st.divider()

                # ★ NOVO: Seção de Errata com seleção de perguntas
                with st.container(border=True):
                    st.markdown("### 🔗 Gerar Errata para o Cliente")
                    st.caption(
                        "Marque abaixo quais perguntas precisam ser revisadas pelo cliente. "
                        "Após salvar, gere o link e envie para ele."
                    )

                    col_eb, col_eu = st.columns(2)

                    with col_eb:
                        st.markdown("**Perguntas Branded**")
                        novas_marc_b = set()
                        for idx, p in enumerate(lista_b):
                            checked = str(idx) in marc_b_atual
                            if st.checkbox(
                                p.get("Pergunta", f"Pergunta {idx+1}"),
                                value=checked,
                                key=f"marc_b_{prot_selecionado}_{idx}"
                            ):
                                novas_marc_b.add(str(idx))

                    with col_eu:
                        st.markdown("**Perguntas Non Branded**")
                        novas_marc_u = set()
                        for idx, p in enumerate(lista_u):
                            checked = str(idx) in marc_u_atual
                            if st.checkbox(
                                p.get("Pergunta", f"Pergunta {idx+1}"),
                                value=checked,
                                key=f"marc_u_{prot_selecionado}_{idx}"
                            ):
                                novas_marc_u.add(str(idx))

                    total_marcadas = len(novas_marc_b) + len(novas_marc_u)

                    col_save, col_link = st.columns([1, 2])

                    with col_save:
                        if st.button(
                            f"💾 Salvar Seleção ({total_marcadas} marcada{'s' if total_marcadas != 1 else ''})",
                            type="primary",
                            use_container_width=True,
                            disabled=(total_marcadas == 0)
                        ):
                            supabase.table("briefings").update({
                                "errata_marcadas_branded":   list(novas_marc_b),
                                "errata_marcadas_unbranded": list(novas_marc_u),
                            }).eq("protocolo", prot_selecionado).execute()
                            st.success("✅ Seleção salva! Agora gere o link abaixo.")
                            st.rerun()

                    with col_link:
                        tem_marcacoes = bool(marc_b_atual or marc_u_atual)
                        if tem_marcacoes:
                            app_url = st.secrets.get("APP_URL", "seu-site.streamlit")
                            link_errata = f"https://{app_url}.app/?errata={prot_selecionado}"
                            st.code(link_errata)
                            st.caption("Copie e envie este link ao cliente.")
                        else:
                            st.info("Salve a seleção de perguntas para gerar o link.")

        else:
            st.info("Nenhum briefing recebido ainda.")

    st.stop()


# ==========================================
# BARRA LATERAL (SIDEBAR) DE PROGRESSO
# ==========================================
if st.session_state.tipo_usuario == 'cliente' and st.session_state.step < 9:
    with st.sidebar:
        img_nexus_sidebar = get_base64_image("logos nexus_negativa tagline (2).png")
        img_voxia_sidebar = get_base64_image("VOXIA - Logo negativo branco.png")

        st.markdown(f"""
<div style="display: flex; justify-content: center; align-items: center; gap: 16px; margin-bottom: 20px; margin-top: 5px; padding-bottom: 20px; border-bottom: 1px solid #2a2a3a;">
<img src="data:image/png;base64,{img_nexus_sidebar}" width="90">
<div style="width: 1px; height: 28px; background-color: #3a3a4a;"></div>
<img src="data:image/png;base64,{img_voxia_sidebar}" width="70">
</div>
""", unsafe_allow_html=True)

        st.markdown("<h2 style='color: #F58220; margin-top: 0px; margin-bottom: 24px; font-size: 1.6rem;'>Progresso do Briefing</h2>", unsafe_allow_html=True)

        etapas = [
            "Contexto da Análise",
            "Pilares de Autoridade",
            "Objetivos Estratégicos",
            "Cenário Competitivo",
            "Atributos da Marca",
            "Busca Institucional",
            "Busca de Mercado",
            "Revisão Final"
        ]

        html_sidebar = ""
        for i, etapa in enumerate(etapas):
            step_idx = i + 1
            if step_idx < st.session_state.step:
                html_sidebar += f'<div class="sidebar-step completed"><div class="circle-check">✓</div> {step_idx}. {etapa}</div>'
            elif step_idx == st.session_state.step:
                html_sidebar += f'<div class="sidebar-step current"><div class="circle-dotted"></div> {step_idx}. {etapa}</div>'
            else:
                html_sidebar += f'<div class="sidebar-step pending"><div class="circle-empty"></div> {step_idx}. {etapa}</div>'

        st.markdown(html_sidebar, unsafe_allow_html=True)


# ==========================================
# FLUXO DO CLIENTE (WIZARD)
# ==========================================

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    st.title("1. Identificação e Contexto")
    st.markdown("Indique o sujeito principal da análise.")

    lista_tipos = ["Uma Marca / Empresa", "Um Porta-voz / Executivo", "Uma Narrativa / Tema de Mercado"]
    idx_tipo = lista_tipos.index(st.session_state.dados['tipo_analise']) if st.session_state.dados['tipo_analise'] in lista_tipos else 0

    st.session_state.dados['tipo_analise'] = st.radio("O que estamos analisando?", lista_tipos, index=idx_tipo)
    st.session_state.dados['empresa'] = st.text_input(
        "Nome da empresa, porta-voz ou tema:",
        value=st.session_state.dados['empresa'],
        placeholder="Ex: Nestlé, Secretário de Saúde, Sustentabilidade na Indústria"
    )

    if st.session_state.dados['tipo_analise'] != "Uma Narrativa / Tema de Mercado":
        st.markdown("As IAs utilizam esse link para medir sua autoridade digital e taxa de citação direta.")
        site_val = st.text_input("Site Oficial:", value=st.session_state.dados['site_url'], placeholder="https://www.suaempresa.com.br")
        st.session_state.dados['site_url'] = site_val
        if site_val and "." not in site_val:
            st.warning("Aviso: Insira um domínio válido.")

    pode_ir = bool(st.session_state.dados['empresa'].strip())
    if st.session_state.dados['tipo_analise'] != "Uma Narrativa / Tema de Mercado":
        pode_ir = pode_ir and bool(st.session_state.dados['site_url'].strip() and "." in st.session_state.dados['site_url'])

    st.divider()
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_a: st.button("Avançar →", on_click=next_step, type="primary", disabled=not pode_ir, use_container_width=True)

# --- PASSO 2 ---
elif st.session_state.step == 2:
    st.title("2. Pilares de Autoridade")
    st.markdown("Qual é a principal mensagem que você quer que a IA entregue ao falar de você?")
    st.info("Ex: 'Somos a empresa que humaniza a tecnologia'. Descreva a narrativa para medirmos o alinhamento das respostas.")

    st.session_state.dados['desc_pilar'] = st.text_area(
        "Descreva detalhadamente:", value=st.session_state.dados['desc_pilar'],
        height=150, label_visibility="collapsed", placeholder="Digite sua narrativa detalhada aqui..."
    )

    st.divider()
    pode_ir = bool(st.session_state.dados['desc_pilar'].strip())
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar", on_click=prev_step, use_container_width=True)
    with col_a: st.button("Avançar →", on_click=next_step, type="primary", disabled=not pode_ir, use_container_width=True)

# --- PASSO 3 ---
elif st.session_state.step == 3:
    st.title("3. Objetivos Estratégicos")
    st.caption("(Selecione no mínimo 1 objetivo)")

    obj_salvos = st.session_state.dados['objetivos']
    obj1 = st.checkbox("Entender percepção atual: Mapeia como as IAs descrevem a marca hoje.", value="Percepção Atual" in obj_salvos)
    obj2 = st.checkbox("Identificar liderança: Analisa recomendações face à concorrência (Share of Voice).", value="Liderança" in obj_salvos)
    obj3 = st.checkbox("Mitigar menções negativas: Identifica 'alucinações' ou associações a crises passadas.", value="Mitigar Crises" in obj_salvos)
    obj4 = st.checkbox("Ampliar influência: Estratégia para tornar os seus porta-vozes a fonte primária dos robôs.", value="Ampliar Influência" in obj_salvos)

    st.session_state.dados['objetivos'] = []
    if obj1: st.session_state.dados['objetivos'].append("Percepção Atual")
    if obj2: st.session_state.dados['objetivos'].append("Liderança")
    if obj3: st.session_state.dados['objetivos'].append("Mitigar Crises")
    if obj4: st.session_state.dados['objetivos'].append("Ampliar Influência")

    st.divider()
    pode_ir = len(st.session_state.dados['objetivos']) > 0
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar", on_click=prev_step, use_container_width=True)
    with col_a:
        if st.button("Avançar →", on_click=next_step, type="primary", disabled=not pode_ir, use_container_width=True): pass
    if not pode_ir: st.error("Aviso: Selecione pelo menos um objetivo estratégico.")

# --- PASSO 4 ---
elif st.session_state.step == 4:
    st.title("4. Cenário Competitivo")
    st.markdown("Liste de 5 a 10 players ou temas concorrentes.")

    tipo = st.session_state.dados['tipo_analise']
    tem_erro_url = False

    with st.container(border=True):
        col_nome, col_site, col_del = st.columns([4, 4, 1])
        with col_nome: st.markdown("<p style='font-weight: bold;'>Nome do Concorrente / Tema</p>", unsafe_allow_html=True)
        with col_site:
            if tipo != "Uma Narrativa / Tema de Mercado":
                st.markdown("<p style='font-weight: bold;'>URL do Concorrente (Obrigatório)</p>", unsafe_allow_html=True)

        for i, item in enumerate(st.session_state.lista_conc):
            c1, c2, c3 = st.columns([4, 4, 1])
            item["nome"] = c1.text_input(f"Nome {i}", value=item["nome"], key=f"cn_{i}", label_visibility="collapsed", placeholder="Ex: Nome da Empresa")
            if tipo != "Uma Narrativa / Tema de Mercado":
                site_val = c2.text_input(f"Site {i}", value=item["site"], key=f"cs_{i}", label_visibility="collapsed", placeholder="https://site.com.br")
                item["site"] = site_val
                if site_val.strip() and "." not in site_val:
                    c2.markdown('<p style="color: #ff4d4d; font-size: 12px; margin-top: -15px;">Link inválido.</p>', unsafe_allow_html=True)
                    tem_erro_url = True
            if c3.button("Remover", key=f"del_c_{i}") and len(st.session_state.lista_conc) > 1:
                st.session_state.lista_conc.pop(i)
                st.rerun()

        if len(st.session_state.lista_conc) < 10:
            if st.button("Adicionar Concorrente"):
                st.session_state.lista_conc.append({"nome": "", "site": ""})
                st.rerun()

    validos = [x for x in st.session_state.lista_conc if x["nome"].strip() and (x["site"].strip() or tipo == "Uma Narrativa / Tema de Mercado")]
    nomes_inseridos = [x["nome"].strip().lower() for x in validos]
    sites_inseridos = [x["site"].strip().lower() for x in validos if x["site"].strip()]
    tem_nome_duplicado = len(nomes_inseridos) != len(set(nomes_inseridos))
    tem_site_duplicado = len(sites_inseridos) != len(set(sites_inseridos))

    btn_ready = len(validos) >= 5 and not tem_erro_url and not tem_nome_duplicado and not tem_site_duplicado

    st.divider()
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar", on_click=prev_step, use_container_width=True)
    with col_a:
        if st.button("Avançar →", on_click=next_step, type="primary", disabled=not btn_ready, use_container_width=True): pass

    if tem_nome_duplicado: st.error("Aviso: Nomes duplicados detectados.")
    if tem_site_duplicado and tipo != "Uma Narrativa / Tema de Mercado": st.error("Aviso: URLs duplicadas detectadas.")
    if tem_erro_url: st.error("Aviso: Corrija os links inválidos.")
    elif len(validos) < 5: st.error(f"Aviso: Faltam {5 - len(validos)} concorrente(s).")

# --- PASSO 5 ---
elif st.session_state.step == 5:
    st.title("5. Atributos da Marca")
    st.markdown("Escolha de 5 a 10 valores para cada lado.")

    col_p, col_n = st.columns(2)

    with col_p:
        st.subheader("Atributos Positivos")
        st.caption("Valores que você deseja que as IAs associem à sua marca.")
        for i, val in enumerate(st.session_state.lista_pos):
            c1, c2 = st.columns([8, 2])
            st.session_state.lista_pos[i] = c1.text_input(f"Pos {i}", value=val, key=f"pos_{i}", label_visibility="collapsed")
            if c2.button("Remover", key=f"del_pos_{i}") and len(st.session_state.lista_pos) > 1:
                st.session_state.lista_pos.pop(i)
                st.rerun()
        if len(st.session_state.lista_pos) < 10:
            if st.button("Adicionar Positivos"):
                st.session_state.lista_pos.append("")
                st.rerun()

    with col_n:
        st.subheader("Atributos Negativos")
        st.caption("Termos que você NÃO quer que as IAs associem à sua marca.")
        for i, val in enumerate(st.session_state.lista_neg):
            c1, c2 = st.columns([8, 2])
            st.session_state.lista_neg[i] = c1.text_input(f"Neg {i}", value=val, key=f"neg_{i}", label_visibility="collapsed")
            if c2.button("Remover", key=f"del_neg_{i}") and len(st.session_state.lista_neg) > 1:
                st.session_state.lista_neg.pop(i)
                st.rerun()
        if len(st.session_state.lista_neg) < 10:
            if st.button("Adicionar Negativos"):
                st.session_state.lista_neg.append("")
                st.rerun()

    st.divider()
    st.markdown("### Justificativa Estratégica")
    st.session_state.dados['justificativa'] = st.text_area(
        "Por que esses atributos são fundamentais para sua estratégia?",
        value=st.session_state.dados['justificativa'],
        placeholder="Como elas ajudam a marca a se diferenciar no mercado?"
    )

    p_validos = len([x for x in st.session_state.lista_pos if x.strip()])
    n_validos = len([x for x in st.session_state.lista_neg if x.strip()])
    pos_unicos = [x.strip().lower() for x in st.session_state.lista_pos if x.strip()]
    neg_unicos = [x.strip().lower() for x in st.session_state.lista_neg if x.strip()]
    tem_pos_dup = len(pos_unicos) != len(set(pos_unicos))
    tem_neg_dup = len(neg_unicos) != len(set(neg_unicos))

    ready = p_validos >= 5 and n_validos >= 5 and st.session_state.dados['justificativa'].strip() and not tem_pos_dup and not tem_neg_dup

    st.divider()
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar", on_click=prev_step, use_container_width=True)
    with col_a:
        if st.button("Avançar →", on_click=next_step, type="primary", disabled=not ready, use_container_width=True): pass

    if tem_pos_dup: st.error("Aviso: Atributos positivos duplicados.")
    if tem_neg_dup: st.error("Aviso: Atributos negativos duplicados.")
    if not ready and not tem_pos_dup and not tem_neg_dup:
        msg_erro = []
        if p_validos < 5: msg_erro.append(f"{5 - p_validos} atributos positivos")
        if n_validos < 5: msg_erro.append(f"{5 - n_validos} atributos negativos")
        if not st.session_state.dados['justificativa'].strip(): msg_erro.append("a justificativa")
        if msg_erro: st.error(f"Aviso: Faltam {', '.join(msg_erro)}.")

# --- PASSO 6 ---
elif st.session_state.step == 6:
    st.title("6. Inteligência de Busca - Institucional")
    marca_parametro = st.session_state.dados['empresa'].strip()

    st.markdown("Cada pergunta será testada nos modelos de IA para auditar sua reputação.")
    st.info(f"Importante: Você deve incluir '{marca_parametro}' em cada pergunta.")

    if st.session_state.limpar_b:
        st.session_state.input_b = ""
        st.session_state.limpar_b = False

    with st.container(border=True):
        new_b = st.text_input("Nova pergunta (Enter para adicionar):", key="input_b", placeholder=f"Ex: A {marca_parametro} é recomendada para...?")
        if st.button("Adicionar Pergunta Branded") or new_b:
            if new_b.strip():
                if marca_parametro.lower() not in new_b.lower():
                    st.error(f"Ação Barrada: '{marca_parametro}' precisa constar na pergunta.")
                elif new_b.strip().lower() in [p.lower() for p in st.session_state.lista_b]:
                    st.error("Ação Barrada: Pergunta duplicada.")
                else:
                    st.session_state.lista_b.insert(0, new_b.strip())
                    st.session_state.limpar_b = True
                    st.rerun()

    for i, p in enumerate(st.session_state.lista_b):
        with st.container():
            st.markdown(f'<div class="card-pergunta"><p style="margin:0;">{p}</p></div>', unsafe_allow_html=True)
            if st.button("Remover", key=f"rb_{i}"):
                st.session_state.lista_b.pop(i)
                st.rerun()

    b_prontos = len(st.session_state.lista_b)
    pode_avancar = b_prontos >= 5

    st.divider()
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar", on_click=prev_step, use_container_width=True)
    with col_a:
        if st.button("Avançar →", on_click=next_step, type="primary", disabled=not pode_avancar, use_container_width=True): pass
    if not pode_avancar:
        st.error(f"Aviso: Faltam {5 - b_prontos} perguntas institucionais.")

# --- PASSO 7 ---
elif st.session_state.step == 7:
    st.title("7. Inteligência de Busca - Mercado")
    marca_parametro = st.session_state.dados['empresa'].strip()

    st.markdown("Meça sua autoridade orgânica no nicho sem citar a marca diretamente.")
    st.warning(f"Atenção: NÃO cite '{marca_parametro}' nestas perguntas.")

    if st.session_state.limpar_u:
        st.session_state.input_u = ""
        st.session_state.limpar_u = False

    with st.container(border=True):
        new_u = st.text_input("Nova pergunta de mercado (Enter):", key="input_u", placeholder="Ex: Qual a melhor empresa de [Setor] no Brasil?")
        if st.button("Adicionar Pergunta de Mercado") or new_u:
            if new_u.strip():
                if marca_parametro.lower() in new_u.lower():
                    st.error(f"Ação Barrada: Remova '{marca_parametro}' da pergunta.")
                elif new_u.strip().lower() in [p.lower() for p in st.session_state.lista_u]:
                    st.error("Ação Barrada: Pergunta duplicada.")
                else:
                    st.session_state.lista_u.insert(0, new_u.strip())
                    st.session_state.limpar_u = True
                    st.rerun()

    for i, p in enumerate(st.session_state.lista_u):
        with st.container():
            st.markdown(f'<div class="card-pergunta"><p style="margin:0;">{p}</p></div>', unsafe_allow_html=True)
            if st.button("Remover", key=f"ru_{i}"):
                st.session_state.lista_u.pop(i)
                st.rerun()

    u_prontos = len(st.session_state.lista_u)
    pode_avancar = u_prontos >= 5

    st.divider()
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar", on_click=prev_step, use_container_width=True)
    with col_a:
        if st.button("Ir para Revisão →", on_click=next_step, type="primary", disabled=not pode_avancar, use_container_width=True): pass
    if not pode_avancar:
        st.error(f"Aviso: Faltam {5 - u_prontos} perguntas de mercado.")

# --- PASSO 8: REVISÃO ---
elif st.session_state.step == 8:
    st.title("8. Revisão Técnica do Briefing")
    st.warning("⚠️ Revise os dados abaixo antes de enviar.")

    with st.container(border=True):
        st.markdown("### 📍 Identidade e Contexto")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.write(f"**Sujeito Principal:** {st.session_state.dados['empresa']}")
            st.write(f"**Tipo de Análise:** {st.session_state.dados['tipo_analise']}")
        with col_r2:
            st.write(f"**Domínio Oficial:** {st.session_state.dados['site_url'] or 'Não informado'}")
            st.write(f"**Objetivos:** {', '.join(st.session_state.dados['objetivos'])}")
        with st.expander("📄 Ver Narrativa"):
            st.write(st.session_state.dados['desc_pilar'])

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### ⚔️ Ecossistema de Mercado")
        col_conc, col_atri = st.columns(2)
        with col_conc:
            st.markdown("**Concorrentes:**")
            for c in [x for x in st.session_state.lista_conc if x['nome'].strip()]:
                st.write(f"• {c['nome']} <span style='color:#666; font-size:12px;'>({c['site']})</span>", unsafe_allow_html=True)
        with col_atri:
            st.markdown("**Atributos:**")
            st.write("**✅ Projetar:** " + ", ".join([x for x in st.session_state.lista_pos if x.strip()]))
            st.write("**❌ Mitigar:** " + ", ".join([x for x in st.session_state.lista_neg if x.strip()]))

    st.markdown("<br>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 🤖 Bateria de Testes")
        st.write(f"**{len(st.session_state.lista_b) + len(st.session_state.lista_u)} perguntas** no total.")
        tab_rev_b, tab_rev_u = st.tabs(["Perguntas Branded", "Perguntas Non Branded"])
        with tab_rev_b:
            for p in st.session_state.lista_b: st.markdown(f"👉 {p}")
        with tab_rev_u:
            for p in st.session_state.lista_u: st.markdown(f"👉 {p}")

    st.divider()
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar e Ajustar", on_click=prev_step, use_container_width=True)
    with col_a: st.button("Dados conferidos →", on_click=next_step, type="primary", use_container_width=True)

# --- PASSO 9: ENVIO ---
elif st.session_state.step == 9:
    st.title("9. Finalização e Envio")

    with st.container(border=True):
        st.session_state.dados['email'] = st.text_input(
            "E-mail para contato sobre os resultados:*",
            value=st.session_state.dados['email'],
            placeholder="seuemail@empresa.com.br"
        )

        st.markdown("#### **Observações Finais**")
        st.markdown("""
            <div style="background-color: #1a1a24; border-left: 4px solid #F58220; padding: 15px; border-radius: 4px; margin-bottom: 10px;">
                <p style="margin: 0; color: #ffffff; font-weight: 500; font-size: 1.1rem;">
                    Há algum detalhe, crise recente ou nuances não abordados?
                </p>
                <p style="margin: 5px 0 0 0; color: #888; font-size: 0.9rem;">
                    Contextos extras ajudam a IA a ser mais precisa e evitar alucinações.
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.session_state.dados['nuances'] = st.text_area(
            "Mensagem adicional:",
            value=st.session_state.dados['nuances'],
            placeholder="Ex: Reestruturação de marca há 2 meses / Foco em investidores...",
            label_visibility="collapsed",
            height=120
        )

        st.checkbox("Aceito os termos de tratamento de dados sensíveis (LGPD).", key="lgpd")

    pode_enviar = st.session_state.get('lgpd', False) and "@" in st.session_state.dados['email']

    st.divider()
    col_v, col_a, _ = st.columns([2, 2, 6])
    with col_v: st.button("← Voltar à Revisão", on_click=prev_step, use_container_width=True)

    with col_a:
        if st.button("FINALIZAR BRIEFING →", type="primary", disabled=not pode_enviar, use_container_width=True):
            descricao_completa = (
                f"E-mail Contato: {st.session_state.dados['email']}\n"
                f"Objetivos: {', '.join(st.session_state.dados['objetivos'])}\n\n"
                f"Narrativa Central: {st.session_state.dados['desc_pilar']}\n\n"
                f"Nuances/Adicional: {st.session_state.dados['nuances']}"
            )
            prot = f"BX-{random.randint(1000, 9999)}"
            supabase.table("briefings").insert({
                "protocolo":        prot,
                "nome_sujeito":     st.session_state.dados['empresa'],
                "tipo_analise":     st.session_state.dados['tipo_analise'],
                "concorrentes":     st.session_state.lista_conc,
                "atributos_pos":    st.session_state.lista_pos,
                "atributos_neg":    st.session_state.lista_neg,
                "contexto_atributos": st.session_state.dados['justificativa'],
                "prompts_branded":  [{"Pergunta": p} for p in st.session_state.lista_b],
                "prompts_unbranded":[{"Pergunta": p} for p in st.session_state.lista_u],
                "descricao":        descricao_completa,
                "status":           "Novo",
                "link_apresentacao": "",
                "errata_marcadas_branded":   [],
                "errata_marcadas_unbranded": [],
            }).execute()

            st.session_state.step = 10
            st.rerun()

# --- PASSO 10: SUCESSO ---
elif st.session_state.step == 10:
    url_destino = "https://nexus.fsb.com.br/"
    html_sucesso = textwrap.dedent(f"""
        <script>
            setTimeout(function() {{
                window.top.location.href = "{url_destino}";
            }}, 5000);
        </script>
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; height: 60vh; font-family: sans-serif;">
            <div style="width: 80px; height: 80px; border-radius: 50%; border: 4px solid #4CAF50; display: flex; justify-content: center; align-items: center; margin-bottom: 20px;">
                <span style="color: #4CAF50; font-size: 50px; font-weight: bold;">✓</span>
            </div>
            <h1 style="color: white; font-size: 2.5rem; margin: 10px 0;">Briefing Enviado!</h1>
            <p style="color: #ccc; font-size: 1.2rem; max-width: 500px; margin-bottom: 30px;">
                Seu diagnóstico foi registrado com sucesso.<br>
                Em instantes você será levado de volta ao portal <strong>Nexus</strong>.
            </p>
            <div style="padding: 20px; background-color: #1a1a24; border-radius: 12px; border: 1px solid #333;">
                <p style="color: #888; font-size: 0.9rem; margin-bottom: 15px;">Não foi redirecionado automaticamente?</p>
                <a href="{url_destino}" target="_top" style="text-decoration: none;">
                    <button style="background-color: #F58220; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 1rem;">
                        Clique aqui para voltar ao site
                    </button>
                </a>
            </div>
        </div>
    """)
    st.markdown(html_sucesso, unsafe_allow_html=True)
    st.balloons()
