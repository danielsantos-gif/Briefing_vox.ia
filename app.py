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

# --- CONTROLE DE NAVEGAÇÃO E ESTADO SEGURO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'acesso_liberado' not in st.session_state: st.session_state.acesso_liberado = False
if 'tipo_usuario' not in st.session_state: st.session_state.tipo_usuario = None

# [CORREÇÃO APLICADA AQUI]: Inicialização de todas as variáveis para impedir o AttributeError
if 'empresa' not in st.session_state: st.session_state.empresa = ""
if 'tipo_analise' not in st.session_state: st.session_state.tipo_analise = "Uma Marca / Empresa"
if 'site_url' not in st.session_state: st.session_state.site_url = ""
if 'desc' not in st.session_state: st.session_state.desc = ""
if 'objetivos' not in st.session_state: st.session_state.objetivos = []
if 'lista_b' not in st.session_state: st.session_state.lista_b = []
if 'lista_u' not in st.session_state: st.session_state.lista_u = []
if 'lista_conc' not in st.session_state: st.session_state.lista_conc = [{"nome": "", "site": ""}] * 5
if 'lista_pos' not in st.session_state: st.session_state.lista_pos = [""] * 5
if 'lista_neg' not in st.session_state: st.session_state.lista_neg = [""] * 5

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
    
    st.subheader("Perguntas Branded")
    branded_ed = st.data_editor(pd.DataFrame(dados['prompts_branded']), use_container_width=True, num_rows="dynamic", key="err_b")
    st.subheader("Perguntas de Mercado (Unbranded)")
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
# LOGIN E APRESENTAÇÃO
# ==========================================
if not st.session_state.acesso_liberado:
    st.markdown("<h1 style='color: #F58220; margin-bottom: -15px;'>Briefing para vox.ia:</h1>", unsafe_allow_html=True)
    st.title("Reputação e Presença de Marca na Inteligência Artificial.")
    st.markdown("Este diagnóstico mapeia a presença da sua marca no ecossistema de IA Generativa. A precisão dos dados a seguir é fundamental para treinarmos nossos modelos de análise e garantir um relatório fiel à sua realidade.")
    
    st.divider()
    
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
# FLUXO DO CLIENTE (WIZARD - 8 PASSOS)
# ==========================================
st.progress(st.session_state.step / 8)

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    st.title("1. Identificação e Contexto")
    st.markdown("Indique o sujeito principal da análise. Pode ser o nome da sua corporação, de um líder específico ou de uma narrativa de mercado que você deseja monitorar.")
    
    st.radio("O que estamos analisando?", 
             ["Uma Marca / Empresa", "Um Porta-voz / Executivo", "Uma Narrativa / Tema de Mercado"], 
             key="tipo_analise")
    
    st.text_input("Nome da empresa, porta-voz ou tema a ser analisado:", key="empresa", placeholder="Ex: Nestlé, Secretário de Saúde, Sustentabilidade na Indústria")
    
    if st.session_state.tipo_analise != "Uma Narrativa / Tema de Mercado":
        st.markdown("As IAs utilizam esse link para medir sua autoridade digital e taxa de citação direta.")
        site_oficial = st.text_input("Site Oficial (Domínio Principal):", key="site_url", placeholder="https://www.suaempresa.com.br")
        if site_oficial and not ("." in site_oficial):
            st.warning("⚠️ Insira um domínio válido.")

    pode_ir = bool(st.session_state.empresa)
    if st.session_state.tipo_analise != "Uma Narrativa / Tema de Mercado":
        pode_ir = pode_ir and bool(st.session_state.get("site_url", "").strip() and "." in st.session_state.get("site_url", ""))
        
    st.button("Avançar", on_click=next_step, type="primary", disabled=not pode_ir)

# --- PASSO 2: PILARES DE AUTORIDADE ---
elif st.session_state.step == 2:
    st.title("2. Pilares de Autoridade (Porta-vozes e Narrativas)")
    st.markdown("A reputação em IA é construída por quem fala e pelo que é dito. Vamos detalhar as teses por trás da marca.")
    
    st.markdown("### Narrativa Central ou 'Tese' da Marca:")
    st.info("Qual é a principal mensagem que você quer que a IA entregue ao falar de você? (Ex: 'Somos a empresa que humaniza a tecnologia'). Descreva a narrativa para que possamos medir o alinhamento das respostas.")
    
    st.text_area("Descreva detalhadamente:", key="desc", height=150, label_visibility="collapsed", placeholder="Digite sua narrativa detalhada aqui...")
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    pode_ir = bool(st.session_state.desc)
    col_a.button("Avançar", on_click=next_step, type="primary", disabled=not pode_ir)

# --- PASSO 3: OBJETIVOS ESTRATÉGICOS ---
elif st.session_state.step == 3:
    st.title("3. Objetivos Estratégicos e Concorrência")
    st.markdown("Nesta etapa, definimos o foco do diagnóstico. Precisamos entender o que você deseja priorizar e contra quem o mercado te compara no ambiente digital.")
    st.caption("(Selecione no mínimo 1 objetivo)")
    
    obj1 = st.checkbox("Entender percepção atual: Mapeia como as IAs descrevem a marca hoje.", value="Percepção Atual" in st.session_state.objetivos)
    obj2 = st.checkbox("Identificar liderança: Analisa recomendações da IA face à concorrência (Share of Voice).", value="Liderança" in st.session_state.objetivos)
    obj3 = st.checkbox("Mitigar menções negativas: Identifica 'alucinações' ou associações a crises passadas.", value="Mitigar Crises" in st.session_state.objetivos)
    obj4 = st.checkbox("Ampliar influência: Estratégia para tornar os seus porta-vozes a fonte primária dos robôs.", value="Ampliar Influência" in st.session_state.objetivos)
    
    # Salva seleções
    st.session_state.objetivos = []
    if obj1: st.session_state.objetivos.append("Percepção Atual")
    if obj2: st.session_state.objetivos.append("Liderança")
    if obj3: st.session_state.objetivos.append("Mitigar Crises")
    if obj4: st.session_state.objetivos.append("Ampliar Influência")

    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    pode_ir = len(st.session_state.objetivos) > 0
    if col_a.button("Avançar", on_click=next_step, type="primary", disabled=not pode_ir): pass
    if not pode_ir: st.error("⚠️ Por favor, selecione pelo menos um objetivo estratégico.")

# --- PASSO 4: CENÁRIO COMPETITIVO ---
elif st.session_state.step == 4:
    st.title("4. Cenário Competitivo")
    st.markdown("Para uma análise precisa de share of voice, precisamos identificar exatamente quem são seus rivais. Liste de 5 a 10 players ou temas.")
    
    tipo = st.session_state.get("tipo_analise", "Uma Marca / Empresa")
    tem_erro_url = False

    with st.container(border=True):
        col_nome, col_site, col_del = st.columns([4, 4, 1])
        with col_nome: st.markdown("**Nome do Concorrente / Tema**")
        with col_site: 
            if tipo != "Uma Narrativa / Tema de Mercado":
                st.markdown("**URL do Concorrente (Obrigatório)**")
        
        for i, item in enumerate(st.session_state.lista_conc):
            c1, c2, c3 = st.columns([4, 4, 1])
            
            item["nome"] = c1.text_input(f"Nome {i}", value=item["nome"], key=f"cn_{i}", label_visibility="collapsed", placeholder="Ex: Nome da Empresa")
            
            if tipo != "Uma Narrativa / Tema de Mercado":
                site_val = c2.text_input(f"Site {i}", value=item["site"], key=f"cs_{i}", label_visibility="collapsed", placeholder="https://site.com.br")
                item["site"] = site_val
                
                if site_val.strip() and "." not in site_val:
                    c2.markdown(f'<p style="color: #ff4d4d; font-size: 12px; margin-top: -15px;">⚠️ Link inválido. Adicione o domínio correto (ex: .com.br)</p>', unsafe_allow_html=True)
                    tem_erro_url = True
                    
            if c3.button("🗑️", key=f"del_c_{i}") and len(st.session_state.lista_conc) > 1:
                st.session_state.lista_conc.pop(i)
                st.rerun()

        if len(st.session_state.lista_conc) < 10:
            if st.button("➕ Adicionar Concorrente"):
                st.session_state.lista_conc.append({"nome": "", "site": ""})
                st.rerun()

    nomes_inseridos = [x["nome"].strip().lower() for x in st.session_state.lista_conc if x["nome"].strip()]
    sites_inseridos = [x["site"].strip().lower() for x in st.session_state.lista_conc if x["site"].strip()]
    
    tem_nome_duplicado = len(nomes_inseridos) != len(set(nomes_inseridos))
    tem_site_duplicado = len(sites_inseridos) != len(set(sites_inseridos))

    validos = [x for x in st.session_state.lista_conc if x["nome"].strip() and (x["site"].strip() or tipo == "Uma Narrativa / Tema de Mercado")]
    btn_ready = len(validos) >= 5 and not tem_erro_url and not tem_nome_duplicado and not tem_site_duplicado
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    if st.button("Avançar", on_click=next_step, type="primary", disabled=not btn_ready): pass
    
    if tem_nome_duplicado:
        st.error("⚠️ Você inseriu concorrentes com o mesmo nome. Por favor, remova as repetições.")
    if tem_site_duplicado and tipo != "Uma Narrativa / Tema de Mercado":
        st.error("⚠️ Você inseriu URLs repetidas. Por favor, remova os sites duplicados.")
    if tem_erro_url:
        st.error("⚠️ Corrija os links inválidos marcados em vermelho para poder avançar.")
    elif len(validos) < 5:
        st.error(f"⚠️ Faltam {5 - len(validos)} concorrente(s) preenchidos para liberar a próxima etapa.")

# --- PASSO 5: ATRIBUTOS DA MARCA ---
elif st.session_state.step == 5:
    st.title("5. Atributos da Marca")
    st.markdown("Escolha de 5 a 10 valores. Estes serão os critérios que usaremos para testar se as IAs reconhecem seus diferenciais reais.")
    
    col_p, col_n = st.columns(2)
    
    with col_p:
        st.subheader("✅ Atributos Positivos")
        st.caption("Liste as variáveis, valores ou adjetivos que você deseja que as IAs associem à sua marca.")
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
        st.caption("Liste as variáveis ou termos que você deseja que as IAs NÃO associem à sua marca.")
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
    st.markdown("**Justificativa Estratégica**")
    st.text_area("Por que esses atributos específicos são fundamentais para sua estratégia?", key="justificativa", placeholder="Como elas ajudam a marca a se diferenciar no mercado?")
    
    p_validos = len([x for x in st.session_state.lista_pos if x.strip()])
    n_validos = len([x for x in st.session_state.lista_neg if x.strip()])
    
    pos_unicos = [x.strip().lower() for x in st.session_state.lista_pos if x.strip()]
    neg_unicos = [x.strip().lower() for x in st.session_state.lista_neg if x.strip()]
    
    tem_pos_duplicado = len(pos_unicos) != len(set(pos_unicos))
    tem_neg_duplicado = len(neg_unicos) != len(set(neg_unicos))
    
    ready = p_validos >= 5 and n_validos >= 5 and st.session_state.get("justificativa", "").strip() != "" and not tem_pos_duplicado and not tem_neg_duplicado
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    if st.button("Avançar", on_click=next_step, type="primary", disabled=not ready): pass
    
    if tem_pos_duplicado:
        st.error("⚠️ Existem atributos positivos repetidos. Por favor, remova as duplicatas.")
    if tem_neg_duplicado:
        st.error("⚠️ Existem atributos negativos repetidos. Por favor, remova as duplicatas.")
        
    if not ready and not tem_pos_duplicado and not tem_neg_duplicado:
        msg_erro = []
        if p_validos < 5: msg_erro.append(f"{5 - p_validos} atributos positivos")
        if n_validos < 5: msg_erro.append(f"{5 - n_validos} atributos negativos")
        if not st.session_state.get("justificativa", "").strip(): msg_erro.append("a justificativa")
        if msg_erro:
            st.error(f"⚠️ Ação Barrada: Faltam {', '.join(msg_erro)}.")

# --- PASSO 6: INTELIGÊNCIA DE BUSCA (BRANDED) ---
elif st.session_state.step == 6:
    st.title("6. Inteligência de Busca - Branded (Institucional)")
    marca_parametro = st.session_state.get("empresa", "Sua Marca").strip()
    
    st.markdown(f"Esta é a fase mais sensível do diagnóstico. Cada pergunta será testada nos modelos de IA para auditar sua reputação.")
    st.info(f"**Importante:** Você deve obrigatoriamente incluir **'{marca_parametro}'** em cada pergunta. Não envie perguntas genéricas; use dúvidas reais que seus clientes possuem.")
    
    with st.container(border=True):
        new_b = st.text_input("Nova pergunta (Aperte Enter para adicionar):", key="in_b", placeholder=f"Ex: A {marca_parametro} é recomendada para projetos...?")
        
        if st.button("➕ Adicionar Pergunta Branded", key="btn_add_b") and new_b:
            if marca_parametro.lower() not in new_b.lower():
                st.error(f"⚠️ Ação Barrada: O termo '{marca_parametro}' precisa obrigatoriamente constar na sua pergunta.")
            elif new_b.strip().lower() in [p.lower() for p in st.session_state.lista_b]:
                st.error("⚠️ Ação Barrada: Esta pergunta já foi adicionada! Por favor, NÃO repita perguntas.")
            else:
                st.session_state.lista_b.insert(0, new_b.strip())
                st.rerun()
            
    for i, p in enumerate(st.session_state.lista_b):
        with st.container():
            st.markdown(f'<div class="card-pergunta">{p}</div>', unsafe_allow_html=True)
            if st.button("Remover", key=f"rb_{i}"):
                st.session_state.lista_b.pop(i)
                st.rerun()

    st.divider()
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    b_prontos = len(st.session_state.lista_b)
    pode_avancar = b_prontos >= 5
    
    if st.button("Avançar para Perguntas de Mercado", on_click=next_step, type="primary", disabled=not pode_avancar): pass
    if not pode_avancar:
        st.error(f"⚠️ Ação Barrada: Faltam {5 - b_prontos} perguntas institucionais para concluir esta etapa.")

# --- PASSO 7: INTELIGÊNCIA DE BUSCA (MERCADO) ---
elif st.session_state.step == 7:
    st.title("7. Inteligência de Busca - Mercado")
    marca_parametro = st.session_state.get("empresa", "Sua Marca").strip()
    
    st.markdown("Aqui medimos a sua autoridade orgânica no nicho. O objetivo é descobrir se as IAs recomendam a sua marca espontaneamente quando um usuário busca por uma solução técnica ou líder de setor.")
    st.warning(f"**Atenção:** Nestas perguntas, você **NÃO** deve citar '{marca_parametro}'. Foque em termos genéricos de mercado e dores que o seu produto resolve.")
    
    with st.container(border=True):
        new_u = st.text_input("Nova pergunta de mercado (Aperte Enter):", key="in_u", placeholder="Ex: Qual a melhor empresa de [Setor] no Brasil?")
        
        if st.button("➕ Adicionar Pergunta de Mercado", key="btn_add_u") and new_u:
            if marca_parametro.lower() in new_u.lower():
                st.error(f"⚠️ Ação Barrada: Remova o termo '{marca_parametro}'. O objetivo aqui é avaliar a recomendação orgânica sem citar a marca.")
            elif new_u.strip().lower() in [p.lower() for p in st.session_state.lista_u]:
                st.error("⚠️ Ação Barrada: Esta pergunta já foi adicionada! Por favor, NÃO repita perguntas.")
            else:
                st.session_state.lista_u.insert(0, new_u.strip())
                st.rerun()
                
    for i, p in enumerate(st.session_state.lista_u):
        with st.container():
            st.markdown(f'<div class="card-pergunta">{p}</div>', unsafe_allow_html=True)
            if st.button("Remover", key=f"ru_{i}"):
                st.session_state.lista_u.pop(i)
                st.rerun()

    st.divider()
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    u_prontos = len(st.session_state.lista_u)
    pode_avancar = u_prontos >= 5
    
    if st.button("Ir para Revisão Final", on_click=next_step, type="primary", disabled=not pode_avancar): pass
    if not pode_avancar:
        st.error(f"⚠️ Ação Barrada: Faltam {5 - u_prontos} perguntas de mercado para concluir o formulário.")

# --- PASSO 8: REVISÃO E ENVIO ---
elif st.session_state.step == 8:
    st.title("8. Revisão e Envio")
    st.markdown("Estamos quase lá! Antes de enviar, certifique-se de que os dados fornecidos refletem a estratégia atual. Uma vez enviado e aprovado, nossa equipe iniciará o processamento dos diagnósticos.")
    
    # Uso seguro do `.get` como camada dupla de segurança para a exibição de dados
    st.write(f"**Sujeito da Análise:** {st.session_state.get('empresa', 'Não informado')}")
    st.write(f"**Prompts Registrados:** {len(st.session_state.get('lista_b', []))} Branded / {len(st.session_state.get('lista_u', []))} Mercado")
    
    st.divider()
    st.markdown("### Contato e Considerações Finais")
    email_contato = st.text_input("E-mail para contato sobre os resultados do produto:*", placeholder="seuemail@empresa.com.br")
    nuances = st.text_area("Há algum detalhe, crise recente ou nuances que não foram abordados nas perguntas anteriores e que você considera vital para nossa análise?", placeholder="Destaque aqui...")
    
    st.checkbox("Aceito os termos de tratamento de dados sensíveis (LGPD).", key="lgpd")
    
    col_v, col_a = st.columns([1, 5])
    col_v.button("Voltar", on_click=prev_step)
    
    pode_enviar = st.session_state.get('lgpd', False) and "@" in email_contato
    
    with col_a:
        if st.button("🚀 FINALIZAR BRIEFING", type="primary", disabled=not pode_enviar):
            descricao_completa = f"E-mail Contato: {email_contato}\nObjetivos: {', '.join(st.session_state.get('objetivos', []))}\n\nNarrativa Central: {st.session_state.get('desc', '')}\n\nNuances/Adicional: {nuances}"
            
            prot = f"BX-{random.randint(1000, 9999)}"
            supabase.table("briefings").insert({
                "protocolo": prot,
                "nome_sujeito": st.session_state.get("empresa", ""),
                "tipo_analise": st.session_state.get("tipo_analise", ""),
                "concorrentes": st.session_state.get("lista_conc", []),
                "prompts_branded": [{"Pergunta": p} for p in st.session_state.get("lista_b", [])],
                "prompts_unbranded": [{"Pergunta": p} for p in st.session_state.get("lista_u", [])],
                "descricao": descricao_completa,
                "status": "Novo"
            }).execute()
            st.success(f"Briefing enviado com sucesso! Nosso time de especialistas entrará em contato. Protocolo: {prot}")
            st.balloons()
        if not pode_enviar:
            st.caption("Preencha um e-mail válido e aceite os termos da LGPD para finalizar.")
