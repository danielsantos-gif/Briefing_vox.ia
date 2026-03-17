import streamlit as st
import pandas as pd
import random
from supabase import create_client

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Briefing | Vox.ia", page_icon="🟠", layout="wide")

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
    </style>
    """, unsafe_allow_html=True)

# --- CONTROLE DE NAVEGAÇÃO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'acesso_liberado' not in st.session_state: st.session_state.acesso_liberado = False
if 'tipo_usuario' not in st.session_state: st.session_state.tipo_usuario = None

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- CABEÇALHO ---
col_l, _, col_r = st.columns([1, 2, 1])
with col_l:
    try: st.image("logos nexus_negativa tagline (2).png", width=150)
    except: st.caption("[Logo Nexus]")
with col_r:
    try: st.image("WhatsApp Image 2026-03-17 at 16.40.54 (1).jpeg", width=120)
    except: st.caption("[Logo Vox.ia]")
st.divider()

# ==========================================
# MÓDULO DE ERRATA (VIA URL)
# ==========================================
if "errata" in st.query_params:
    id_prot = st.query_params["errata"]
    st.title("📝 Correção de Briefing")
    
    res = supabase.table("briefings").select("*").eq("protocolo", id_prot).execute()
    if not res.data:
        st.error("Protocolo não encontrado.")
        st.stop()
        
    dados = res.data[0]
    st.warning(f"Ajuste os prompts para: {dados['nome_sujeito']}. O novo envio substituirá o antigo.")
    
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
# LOGIN
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
# PAINEL ADMIN (DASHBOARD)
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
        st.subheader("Indicadores-Chave")
        c1, c2 = st.columns(2)
        c1.metric("Total de Briefings", len(res_adm.data) if res_adm.data else 0)
        c2.metric("Taxa de Errata", "15%")
        st.bar_chart(pd.DataFrame({"Volume": [10, 20, 15]}, index=["Marca", "Porta-voz", "Narrativa"]))
    
    if st.button("Sair"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# ==========================================
# FLUXO DO CLIENTE (WIZARD)
# ==========================================
st.progress(st.session_state.step / 5)

# --- PASSO 1 ---
if st.session_state.step == 1:
    st.title("1. Identificação e Contexto")
    st.markdown("A reputação em IA é construída por quem fala e pelo que é dito. Vamos detalhar as teses por trás da marca. [cite: 1205, 1206]")
    
    st.radio("O que estamos analisando?", 
             ["Uma Marca / Empresa", "Um Porta-voz / Executivo", "Uma Narrativa / Tema de Mercado"], 
             key="tipo_analise")
    
    st.text_input("Nome do sujeito principal:", key="empresa", placeholder="Ex: Nestlé, Secretário de Saúde, Sustentabilidade [cite: 1187]")
    
    if st.session_state.tipo_analise != "Uma Narrativa / Tema de Mercado":
        site_oficial = st.text_input("Site Oficial (Domínio Principal):", key="site_url", placeholder="https://www.suaempresa.com.br")
        if site_oficial and not ("." in site_oficial):
            st.warning("⚠️ Insira um domínio válido.")

    st.text_area("Narrativa Central / Objetivo:", key="desc", 
                 placeholder="Qual é a principal mensagem que você quer que a IA entregue ao falar de você? [cite: 1209]")
    
    pode_ir = st.session_state.empresa and st.session_state.desc
    st.button("Avançar", on_click=next_step, type="primary", disabled=not pode_ir)

# --- PASSO 2 ---
elif st.session_state.step == 2:
    st.title("2. Cenário Competitivo")
    st.markdown("Para uma análise precisa de share of voice, precisamos identificar exatamente quem são seus rivais. ")
    
    tipo = st.session_state.get("tipo_analise", "Uma Marca / Empresa")
    
    if 'lista_conc' not in st.session_state:
        st.session_state.lista_conc = [{"nome": "", "site": ""}] * 5

    with st.container(border=True):
        # Títulos fixos das colunas
        col_nome, col_site, col_del = st.columns([4, 4, 1])
        with col_nome: st.markdown("**Nome do Concorrente / Tema**")
        with col_site: 
            if tipo != "Uma Narrativa / Tema de Mercado":
                st.markdown("**URL do Concorrente (Obrigatório)**")
        
        for i, item in enumerate(st.session_state.lista_conc):
            c1, c2, c3 = st.columns([4, 4, 1])
            
            item["nome"] = c1.text_input(f"Nome {i}", value=item["nome"], key=f"cn_{i}", label_visibility="collapsed", placeholder="Nome")
            
            if tipo != "Uma Narrativa / Tema de Mercado":
                site_val = c2.text_input(f"Site {i}", value=item["site"], key=f"cs_{i}", label_visibility="collapsed", placeholder="https://site.com.br")
                if site_val and "." not in site_val:
                    c2.markdown(f'<p style="color: #ff4d4d; font-size: 12px; margin-top: -15px;">⚠️ Link inválido</p>', unsafe_allow_html=True)
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

    # Validação dinâmica e aviso claro
    validos = [x for x in st.session_state.lista_conc if x["nome"].strip() and (x["site"].strip() or tipo == "Uma Narrativa / Tema de Mercado")]
    btn_ready = len(validos) >= 5
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    if st.button("Avançar", on_click=next_step, type="primary", disabled=not btn_ready): pass
    if not btn_ready:
        faltam = 5 - len(validos)
        st.error(f"⚠️ Faltam {faltam} concorrente(s) com dados válidos para liberar a próxima etapa.")

# --- PASSO 3 ---
elif st.session_state.step == 3:
    st.title("3. Atributos da Marca")
    st.markdown("Escolha de 5 a 10 valores. Estes serão os critérios que usaremos para testar se as IAs reconhecem seus diferenciais reais. [cite: 1340, 1376]")
    
    col_p, col_n = st.columns(2)
    
    with col_p:
        st.subheader("✅ Atributos Positivos")
        st.caption("Liste as variáveis, valores ou adjetivos que você deseja que as IAs associem à sua marca. [cite: 1337]")
        if "lista_pos" not in st.session_state: st.session_state.lista_pos = [""] * 5
        
        for i, val in enumerate(st.session_state.lista_pos):
            c1, c2 = st.columns([8, 2])
            st.session_state.lista_pos[i] = c1.text_input(f"Pos {i}", value=val, key=f"pos_{i}", label_visibility="collapsed")
            if c2.button("🗑️", key=f"del_pos_{i}") and len(st.session_state.lista_pos) > 1:
                st.session_state.lista_pos.pop(i)
                st.rerun()
        
        if len(st.session_state.lista_pos) < 10:
            if st.button("➕ Adicionar Positivos"):
                st.session_state.lista_pos.append("")
                st.rerun()
                
    with col_n:
        st.subheader("❌ Atributos Negativos")
        st.caption("Liste as variáveis ou termos que você deseja que as IAs NÃO associem à sua marca... [cite: 1373]")
        if "lista_neg" not in st.session_state: st.session_state.lista_neg = [""] * 5
        
        for i, val in enumerate(st.session_state.lista_neg):
            c1, c2 = st.columns([8, 2])
            st.session_state.lista_neg[i] = c1.text_input(f"Neg {i}", value=val, key=f"neg_{i}", label_visibility="collapsed")
            if c2.button("🗑️", key=f"del_neg_{i}") and len(st.session_state.lista_neg) > 1:
                st.session_state.lista_neg.pop(i)
                st.rerun()
        
        if len(st.session_state.lista_neg) < 10:
            if st.button("➕ Adicionar Negativos"):
                st.session_state.lista_neg.append("")
                st.rerun()

    st.divider()
    st.markdown("**Justificativa dos Atributos Positivos e Negativos**")
    st.text_area("Por que esses atributos específicos são fundamentais para sua estratégia? [cite: 1365, 1366]", key="justificativa", placeholder="Explique o contexto estratégico...")
    
    p_validos = len([x for x in st.session_state.lista_pos if x.strip()])
    n_validos = len([x for x in st.session_state.lista_neg if x.strip()])
    ready = p_validos >= 5 and n_validos >= 5 and st.session_state.get("justificativa", "").strip() != ""
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    if st.button("Avançar", on_click=next_step, type="primary", disabled=not ready): pass
    if not ready:
        faltam_p = max(0, 5 - p_validos)
        faltam_n = max(0, 5 - n_validos)
        msg_erro = []
        if faltam_p > 0: msg_erro.append(f"{faltam_p} atributos positivos")
        if faltam_n > 0: msg_erro.append(f"{faltam_n} atributos negativos")
        if not st.session_state.get("justificativa", "").strip(): msg_erro.append("a justificativa estratégica")
        st.error(f"⚠️ Falta preencher: {', '.join(msg_erro)}.")

# --- PASSO 4 ---
elif st.session_state.step == 4:
    st.title("4. Inteligência de Busca")
    st.markdown("Esta é a fase mais sensível do diagnóstico. Cada pergunta abaixo será testada individualmente nos modelos de IA para auditar sua reputação. [cite: 1388]")
    
    marca_parametro = st.session_state.get("empresa", "Sua Marca").strip()
    marca_lower = marca_parametro.lower()
    
    aba_branded, aba_unbranded = st.tabs(["🔍 1. Com a sua Marca (Branded)", "🌐 2. De Mercado (Unbranded)"])
    
    # ABA A: BRANDED
    with aba_branded:
        st.info("Importante: Como os testes são isolados, você deve obrigatoriamente incluir o nome da empresa ou do porta-voz em cada pergunta. ")
        if 'lista_b' not in st.session_state: st.session_state.lista_b = []
        
        with st.container(border=True):
            new_b = st.text_input("Nova pergunta Branded (Aperte Enter para adicionar):", key="in_b", placeholder=f"Ex: A {marca_parametro} é recomendada para projetos...?")
            
            if st.button("Adicionar à Lista Branded", key="btn_add_b") and new_b:
                if marca_lower not in new_b.lower():
                    st.error(f"⚠️ Ação Barrada: O termo '{marca_parametro}' precisa constar na pergunta.")
                elif new_b.strip().lower() in [p.lower() for p in st.session_state.lista_b]:
                    st.error("⚠️ Esta pergunta já foi adicionada! Por favor, NÃO repita perguntas. ")
                else:
                    st.session_state.lista_b.insert(0, new_b.strip())
                    st.rerun()
                
        for i, p in enumerate(st.session_state.lista_b):
            with st.container():
                st.markdown(f'<div class="card-pergunta">{p}</div>', unsafe_allow_html=True)
                if st.button("Remover", key=f"rb_{i}"):
                    st.session_state.lista_b.pop(i)
                    st.rerun()

    # ABA B: UNBRANDED
    with aba_unbranded:
        st.warning("Aqui medimos a sua autoridade orgânica no nicho. O objetivo é descobrir se os modelos de IA recomendam a sua marca espontaneamente... [cite: 1750] Importante: Nestas perguntas, você NÃO deve citar o seu próprio nome. [cite: 1752]")
        if 'lista_u' not in st.session_state: st.session_state.lista_u = []
        
        with st.container(border=True):
            new_u = st.text_input("Nova pergunta de Mercado (Aperte Enter):", key="in_u", placeholder="Ex: Qual a melhor empresa de [Setor] no Brasil?")
            
            if st.button("Adicionar à Lista de Mercado", key="btn_add_u") and new_u:
                if marca_lower in new_u.lower():
                    st.error(f"⚠️ Ação Barrada: Remova o termo '{marca_parametro}'. Foque em termos genéricos de mercado e dores que o seu produto resolve. [cite: 1753]")
                elif new_u.strip().lower() in [p.lower() for p in st.session_state.lista_u]:
                    st.error("⚠️ Esta pergunta já foi adicionada! Por favor, NÃO repita perguntas. [cite: 1762]")
                else:
                    st.session_state.lista_u.insert(0, new_u.strip())
                    st.rerun()
                    
        for i, p in enumerate(st.session_state.lista_u):
            with st.container():
                st.markdown(f'<div class="card-pergunta">{p}</div>', unsafe_allow_html=True)
                if st.button("Remover", key=f"ru_{i}"):
                    st.session_state.lista_u.pop(i)
                    st.rerun()

    # Validações de Envio da Página 4
    st.divider()
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    b_prontos = len(st.session_state.lista_b)
    u_prontos = len(st.session_state.lista_u)
    pode_enviar_prompts = b_prontos >= 5 and u_prontos >= 5
    
    if st.button("Revisar Envio", on_click=next_step, type="primary", disabled=not pode_enviar_prompts): pass
    if not pode_enviar_prompts:
        faltam_b = max(0, 5 - b_prontos)
        faltam_u = max(0, 5 - u_prontos)
        msg_prompts = []
        if faltam_b > 0: msg_prompts.append(f"{faltam_b} prompts Branded")
        if faltam_u > 0: msg_prompts.append(f"{faltam_u} prompts de Mercado")
        st.error(f"⚠️ Para avançar, adicione as perguntas mínimas. Faltam: {', '.join(msg_prompts)}.")

# --- PASSO 5 ---
elif st.session_state.step == 5:
    st.title("5. Revisão e Envio")
    st.markdown("Estamos quase lá! Antes de enviar, certifique-se de que os dados fornecidos refletem a estratégia atual da sua marca. [cite: 2109, 2110]")
    
    st.write(f"**Sujeito:** {st.session_state.empresa}")
    st.write(f"**Prompts:** {len(st.session_state.lista_b)} Branded / {len(st.session_state.lista_u)} Mercado")
    
    st.text_area("Há algum detalhe, crise recente ou nuances que não foram abordados nas perguntas anteriores e que você considera vital para nossa análise? [cite: 2114]", key="nuances", placeholder="Destaque aqui...")
    
    st.checkbox("Aceito os termos de tratamento de dados (LGPD).", key="lgpd")
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    with col_a:
        if st.button("🚀 FINALIZAR BRIEFING", type="primary", disabled=not st.session_state.get('lgpd', False)):
            prot = f"BX-{random.randint(1000, 9999)}"
            supabase.table("briefings").insert({
                "protocolo": prot,
                "nome_sujeito": st.session_state.get("empresa"),
                "tipo_analise": st.session_state.get("tipo_analise"),
                "concorrentes": st.session_state.lista_conc,
                "prompts_branded": [{"Pergunta": p} for p in st.session_state.lista_b],
                "prompts_unbranded": [{"Pergunta": p} for p in st.session_state.lista_u],
                "status": "Novo",
                "descricao": st.session_state.get("nuances", "")
            }).execute()
            st.success(f"Briefing enviado com sucesso! Protocolo: {prot}")
            st.balloons()

