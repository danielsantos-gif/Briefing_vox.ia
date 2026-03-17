import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO INICIAL ---
st.set_page_config(page_title="Briefing | Vox.ia", page_icon="🟠", layout="centered")

# Inicialização do controle de passos no Session State
if 'step' not in st.session_state:
    st.session_state.step = 1

def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# --- CABEÇALHO COM LOGOS ---
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    try:
        # Puxando a logo da Nexus
        st.image("assets/logos nexus_negativa tagline (2).png", width=150)
    except:
        st.caption("[Logo Nexus]")
with col3:
    try:
        # Puxando a logo branca da Vox.ia
        st.image("assets/WhatsApp Image 2026-03-17 at 16.40.54 (1).jpeg", width=120) 
    except:
        st.caption("[Logo Vox.ia]")

st.divider()

# --- BARRA DE PROGRESSO ---
progress = st.progress(st.session_state.step / 5)
st.caption(f"Passo {st.session_state.step} de 5")

# ==========================================
# PASSO 1: CONTEXTO DA EMPRESA
# ==========================================
if st.session_state.step == 1:
    st.title("1. Contexto da Marca")
    st.markdown("Precisamos entender quem você é no ecossistema digital.")
    
    empresa = st.text_input("Qual o sujeito principal da análise?", placeholder="Nome da sua empresa, porta-voz ou tema", key="empresa")
    site = st.text_input("Site Oficial (Domínio Principal)", placeholder="https://www.suamarca.com.br", key="site", help="As IAs usam este link para medir sua autoridade digital.")
    desc = st.text_area("Descrição do Negócio", placeholder="Descreva detalhadamente o que você faz, principais produtos e público-alvo.", key="desc")
    
    if st.button("Avançar", on_click=next_step, type="primary"):
        pass

# ==========================================
# PASSO 2: CONCORRENTES
# ==========================================
elif st.session_state.step == 2:
    st.title("2. Cenário Competitivo")
    st.markdown("Quem disputa a atenção do seu cliente? Liste contra quem devemos comparar sua performance.")
    st.caption("A tabela abaixo permite adicionar quantas linhas você precisar (recomendado de 5 a 10). Clique na linha vazia para adicionar.")
    
    # DataFrame inicial vazio para a tabela interativa
    if 'df_concorrentes' not in st.session_state:
        st.session_state.df_concorrentes = pd.DataFrame([{"Nome do Concorrente": "", "Site Oficial": ""}])
    
    st.session_state.df_concorrentes = st.data_editor(
        st.session_state.df_concorrentes,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True
    )
    
    colA, colB = st.columns([1, 5])
    with colA:
        st.button("Voltar", on_click=prev_step)
    with colB:
        st.button("Avançar", on_click=next_step, type="primary")

# ==========================================
# PASSO 3: ATRIBUTOS DA MARCA
# ==========================================
elif st.session_state.step == 3:
    st.title("3. Atributos da Marca")
    st.markdown("O que a IA deve (ou não deve) falar sobre você?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("✅ **O que deseja projetar?**")
        st.caption("Ex: Inovador, Confiável, Rápido")
        pos_attrs = st.text_area("Atributos Positivos (1 por linha)", height=150, key="pos")
    
    with col2:
        st.markdown("❌ **O que deseja mitigar?**")
        st.caption("Ex: Burocrático, Lento, Caro")
        neg_attrs = st.text_area("Atributos Negativos (1 por linha)", height=150, key="neg")
        
    st.text_input("Qual o contexto estratégico por trás dessas escolhas?", key="justificativa", placeholder="Como esses atributos ajudam a diferenciar sua marca?")
    
    colA, colB = st.columns([1, 5])
    with colA:
        st.button("Voltar", on_click=prev_step)
    with colB:
        st.button("Avançar", on_click=next_step, type="primary")

# ==========================================
# PASSO 4: INTELIGÊNCIA DE BUSCA (PROMPTS)
# ==========================================
elif st.session_state.step == 4:
    st.title("4. Dúvidas dos Clientes (Prompts)")
    st.markdown("Adicione as perguntas que testaremos nas IAs. **Não repita perguntas.**")
    
    st.subheader("A. Com a sua Marca (Branded)")
    st.info("Nesta tabela, o nome da sua empresa ou porta-voz **obrigatoriamente** precisa estar na frase.")
    if 'df_branded' not in st.session_state:
        st.session_state.df_branded = pd.DataFrame([{"Pergunta (Citando sua Marca)": ""}])
    
    st.session_state.df_branded = st.data_editor(st.session_state.df_branded, num_rows="dynamic", use_container_width=True, hide_index=True)

    st.subheader("B. Dúvidas de Mercado (Unbranded)")
    st.warning("Nesta tabela, **NÃO cite sua marca**. Testaremos se a IA recomenda você organicamente.")
    if 'df_unbranded' not in st.session_state:
        st.session_state.df_unbranded = pd.DataFrame([{"Pergunta (Genérica/Mercado)": ""}])
    
    st.session_state.df_unbranded = st.data_editor(st.session_state.df_unbranded, num_rows="dynamic", use_container_width=True, hide_index=True)

    colA, colB = st.columns([1, 5])
    with colA:
        st.button("Voltar", on_click=prev_step)
    with colB:
        st.button("Revisar e Enviar", on_click=next_step, type="primary")

# ==========================================
# PASSO 5: REVISÃO E ENVIO
# ==========================================
elif st.session_state.step == 5:
    st.title("5. Revisão Final")
    st.markdown("Confira os dados antes de iniciar o diagnóstico.")
    
    with st.container(border=True):
        st.markdown(f"**Empresa/Tema:** {st.session_state.get('empresa', 'Não preenchido')}")
        st.markdown(f"**Site:** {st.session_state.get('site', 'Não preenchido')}")
        
        comp_count = len(st.session_state.df_concorrentes[st.session_state.df_concorrentes["Nome do Concorrente"] != ""])
        st.markdown(f"**Concorrentes mapeados:** {comp_count}")
        
        brand_count = len(st.session_state.df_branded[st.session_state.df_branded["Pergunta (Citando sua Marca)"] != ""])
        unbrand_count = len(st.session_state.df_unbranded[st.session_state.df_unbranded["Pergunta (Genérica/Mercado)"] != ""])
        st.markdown(f"**Prompts Branded:** {brand_count} | **Prompts de Mercado:** {unbrand_count}")
    
    st.checkbox("Declaro que os dados fornecidos estão corretos e concordo com a análise via IA (LGPD).", key="lgpd")
    
    colA, colB = st.columns([1, 5])
    with colA:
        st.button("Voltar", on_click=prev_step)
    with colB:
        if st.button("🚀 Enviar Diagnóstico", type="primary", disabled=not st.session_state.get('lgpd', False)):
            st.success("Briefing enviado com sucesso! Nossa equipe iniciará o processamento.")
            st.balloons()
