import streamlit as st
import pandas as pd
import random
import time
import uuid
from supabase import create_client, Client

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

# ==========================================
# 1. MÓDULO DE ERRATA (ROTEAMENTO POR URL)
# ==========================================
if "errata" in st.query_params:
    id_briefing = st.query_params["errata"]
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        try: st.image("logos nexus_negativa tagline (2).png", width=150)
        except: st.caption("[Logo Nexus]")
    
    st.divider()
    st.title("📝 Correção de Briefing")
    st.markdown(f"**Protocolo:** `{id_briefing}`")
    
    # Puxar os dados reais deste protocolo
    resposta = supabase.table("briefings").select("*").eq("protocolo", id_briefing).execute()
    
    if not resposta.data:
        st.error("Protocolo não encontrado. Verifique o link enviado pela equipe.")
        st.stop()
        
    dados_errata = resposta.data[0]
    
    st.warning(f"Olá! Analisamos os dados enviados para **{dados_errata['nome_sujeito']}** e precisamos de alguns ajustes nos prompts. Edite as tabelas abaixo e reenvie.")
    
    st.subheader("A. Seus Prompts com a Marca (Branded)")
    df_errata_branded = pd.DataFrame(dados_errata.get("prompts_branded", [{"Pergunta": ""}]))
    df_errata_branded = st.data_editor(df_errata_branded, num_rows="dynamic", use_container_width=True, hide_index=True, key="edit_branded")
    
    st.subheader("B. Seus Prompts de Mercado (Unbranded)")
    df_errata_unbranded = pd.DataFrame(dados_errata.get("prompts_unbranded", [{"Pergunta": ""}]))
    df_errata_unbranded = st.data_editor(df_errata_unbranded, num_rows="dynamic", use_container_width=True, hide_index=True, key="edit_unbranded")
    
    if st.button("Salvar Correções e Reenviar", type="primary"):
        # Atualizar no banco de dados (Update)
        supabase.table("briefings").update({
            "prompts_branded": df_errata_branded.to_dict('records'),
            "prompts_unbranded": df_errata_unbranded.to_dict('records'),
            "status": "Corrigido"
        }).eq("protocolo", id_briefing).execute()
        
        st.success("Perguntas corrigidas com sucesso! A equipe da Vox.ia já foi notificada.")
        st.balloons()
        
    st.stop()

# ==========================================
# CONTROLE DE ESTADO E LOGIN (FLUXO NORMAL)
# ==========================================
if 'acesso_liberado' not in st.session_state:
    st.session_state.acesso_liberado = False
if 'tipo_usuario' not in st.session_state:
    st.session_state.tipo_usuario = None
if 'step' not in st.session_state:
    st.session_state.step = 1

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    try: st.image("logos nexus_negativa tagline (2).png", width=150)
    except: st.caption("[Logo Nexus]")
with col3:
    try: st.image("WhatsApp Image 2026-03-17 at 16.40.54 (1).jpeg", width=120) 
    except: st.caption("[Logo Vox.ia]")
st.divider()

if not st.session_state.acesso_liberado:
    st.title("🔒 Acesso Restrito")
    aba_cliente, aba_admin = st.tabs(["Sou Cliente", "Equipe Nexus (Admin)"])
    
    with aba_cliente:
        senha_cliente = st.text_input("Senha de acesso", type="password")
        if st.button("Acessar Briefing", type="primary"):
            if senha_cliente == "nexus123#":
                st.session_state.acesso_liberado = True
                st.session_state.tipo_usuario = "cliente"
                st.rerun()
            else:
                st.error("Senha incorreta.")
                
    with aba_admin:
        codigo_digitado = st.text_input("Digite o código de 6 dígitos", type="password", help="Simulação: digite 123456")
        if st.button("Validar e Entrar", type="primary"):
            if codigo_digitado == "123456":
                st.session_state.acesso_liberado = True
                st.session_state.tipo_usuario = "admin"
                st.rerun()
            else:
                st.error("Código inválido.")
    st.stop()

# ==========================================
# 2. ÁREA DO ADMIN (DASHBOARD)
# ==========================================
if st.session_state.tipo_usuario == "admin":
    st.title("⚙️ Painel de Controle Vox.ia")
    
    aba_gestao, aba_dashboard = st.tabs(["Gestão de Briefings", "Visão Macro"])
    
    with aba_gestao:
        st.subheader("Briefings Recebidos")
        # Puxa os dados reais do Supabase
        res = supabase.table("briefings").select("protocolo, data_envio, nome_sujeito, tipo_analise, status").order("id", desc=True).execute()
        
        if res.data:
            df_admin = pd.DataFrame(res.data)
            # Formatar a data para ficar bonita
            df_admin['data_envio'] = pd.to_datetime(df_admin['data_envio']).dt.strftime('%d/%m/%Y %H:%M')
            st.dataframe(df_admin, use_container_width=True, hide_index=True)
            
            st.markdown("### Gerador de Link de Errata")
            st.markdown("Copie o protocolo acima e gere o link para enviar ao cliente:")
            prot_errata = st.text_input("Digite o Protocolo (Ex: BX-1234)")
            if prot_errata:
                link = f"https://briefing-voxia.streamlit.app/?errata={prot_errata.strip()}"
                st.code(link, language="html")
        else:
            st.info("Nenhum briefing recebido ainda.")

    with aba_dashboard:
        st.subheader("Inteligência Estratégica")
        st.info("Gráficos ilustrativos. Conforme os dados reais entrarem, estes gráficos serão alimentados pela coluna 'atributos' do banco.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Briefings no Banco", len(res.data) if res.data else 0)
        col2.metric("NPS Médio Estimado", "8.5")
        col3.metric("Taxa de Errata", "15%")

    if st.button("Sair / Logout"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# ==========================================
# 3. ÁREA DO CLIENTE (FORMULÁRIO WIZARD)
# ==========================================
progress = st.progress(st.session_state.step / 5)
st.caption(f"Passo {st.session_state.step} de 5")

# --- PASSO 1 ---
if st.session_state.step == 1:
    st.title("1. Contexto Estratégico")
    st.radio("O que estamos analisando?", ["Uma Marca / Empresa", "Um Porta-voz / Executivo", "Uma Narrativa / Tema de Mercado"], key="tipo_analise")
    st.text_input("Qual o nome do sujeito principal?", key="empresa")
    if st.session_state.tipo_analise == "Uma Marca / Empresa":
        st.text_input("Site Oficial (Domínio Principal)", key="site")
    st.text_area("Descrição / Contexto", key="desc")
    if st.button("Avançar", on_click=next_step, type="primary"): pass

# --- PASSO 2 ---
elif st.session_state.step == 2:
    st.title("2. Cenário Competitivo")
    if st.session_state.tipo_analise == "Uma Narrativa / Tema de Mercado":
        st.markdown("Quais são as narrativas contrárias?")
        if 'df_concorrentes' not in st.session_state: st.session_state.df_concorrentes = pd.DataFrame([{"Temas Concorrentes": ""}])
    else:
        st.markdown("Quem disputa a atenção do seu cliente?")
        if 'df_concorrentes' not in st.session_state: st.session_state.df_concorrentes = pd.DataFrame([{"Nome do Concorrente": "", "Site Oficial (Opcional)": ""}])
            
    st.session_state.df_concorrentes = st.data_editor(st.session_state.df_concorrentes, num_rows="dynamic", use_container_width=True, hide_index=True)
    colA, colB = st.columns([1, 5])
    with colA: st.button("Voltar", on_click=prev_step)
    with colB: st.button("Avançar", on_click=next_step, type="primary")

# --- PASSO 3 ---
elif st.session_state.step == 3:
    st.title("3. Atributos")
    col1, col2 = st.columns(2)
    with col1: st.text_area("✅ Projetar (1 por linha)", height=150, key="pos")
    with col2: st.text_area("❌ Mitigar (1 por linha)", height=150, key="neg")
    st.text_input("Contexto por trás dessas escolhas?", key="justificativa")
    colA, colB = st.columns([1, 5])
    with colA: st.button("Voltar", on_click=prev_step)
    with colB: st.button("Avançar", on_click=next_step, type="primary")

# --- PASSO 4 ---
elif st.session_state.step == 4:
    st.title("4. Inteligência de Busca")
    nome_sujeito = st.session_state.get("empresa", "").strip().lower()
    
    st.subheader("A. Branded (Com Marca)")
    if 'df_branded' not in st.session_state: st.session_state.df_branded = pd.DataFrame([{"Pergunta": ""}])
    st.session_state.df_branded = st.data_editor(st.session_state.df_branded, num_rows="dynamic", use_container_width=True, hide_index=True)
    
    tem_erro_branded = False
    if nome_sujeito:
        for p in st.session_state.df_branded["Pergunta"]:
            if p.strip() and nome_sujeito not in p.lower(): tem_erro_branded = True
    if tem_erro_branded:
        st.markdown(f'<div style="background-color: #3b1c1c; color: #ff9999; padding: 12px; border-radius: 8px;">💡 <b>Sugestão:</b> Notamos que algumas perguntas não citam "{nome_sujeito.title()}". É recomendado citar a marca.</div><br>', unsafe_allow_html=True)

    st.subheader("B. Unbranded (Mercado)")
    if 'df_unbranded' not in st.session_state: st.session_state.df_unbranded = pd.DataFrame([{"Pergunta": ""}])
    st.session_state.df_unbranded = st.data_editor(st.session_state.df_unbranded, num_rows="dynamic", use_container_width=True, hide_index=True)

    colA, colB = st.columns([1, 5])
    with colA: st.button("Voltar", on_click=prev_step)
    with colB: st.button("Revisar e Enviar", on_click=next_step, type="primary")

# --- PASSO 5 (ENVIO PARA O BANCO DE DADOS) ---
elif st.session_state.step == 5:
    st.title("5. Revisão Final")
    st.markdown("Confira os dados antes de enviar.")
    st.checkbox("Declaro que os dados fornecidos estão corretos (LGPD).", key="lgpd")
    
    colA, colB = st.columns([1, 5])
    with colA: st.button("Voltar", on_click=prev_step)
    with colB:
        if st.button("🚀 Enviar Diagnóstico", type="primary", disabled=not st.session_state.get('lgpd', False)):
            with st.spinner("Salvando no banco de dados seguro..."):
                # Gera um protocolo único
                protocolo_gerado = f"BX-{random.randint(1000, 9999)}"
                
                # Prepara as listas (tirando espaços vazios)
                lista_pos = [x.strip() for x in st.session_state.get('pos','').split('\n') if x.strip()]
                lista_neg = [x.strip() for x in st.session_state.get('neg','').split('\n') if x.strip()]
                
                # Monta o pacote de dados exato para o Supabase
                dados_para_salvar = {
                    "protocolo": protocolo_gerado,
                    "tipo_analise": st.session_state.get("tipo_analise", ""),
                    "nome_sujeito": st.session_state.get("empresa", ""),
                    "site_oficial": st.session_state.get("site", ""),
                    "descricao": st.session_state.get("desc", ""),
                    "concorrentes": st.session_state.df_concorrentes.to_dict('records'),
                    "atributos_pos": lista_pos,
                    "atributos_neg": lista_neg,
                    "contexto_atributos": st.session_state.get("justificativa", ""),
                    "prompts_branded": st.session_state.df_branded.to_dict('records'),
                    "prompts_unbranded": st.session_state.df_unbranded.to_dict('records'),
                    "status": "Novo"
                }
                
                # Atira para o banco de dados!
                supabase.table("briefings").insert(dados_para_salvar).execute()
                
            st.success(f"Sucesso! Seu protocolo é o **{protocolo_gerado}**.")
            st.balloons()
