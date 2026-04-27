import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

from modules.database import carregar_dados, carregar_lista_auxiliar, conectar_google_sheets
from modules.logic import verificar_conflito_sala, verificar_disponibilidade_recursos, TOTAL_CHROMEBOOKS, TOTAL_NOTEBOOKS
from modules.relatorio import gerar_imagem_ensalamento



# CONFIGURAÇÃO DA PÁGINA

st.set_page_config(
    page_title="Gestão de Salas | SENAI HUB",
    page_icon="assets/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

if 'logado' not in st.session_state:
    st.session_state['logado'] = False

if not st.session_state['logado']:
    
    
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """, unsafe_allow_html=True)
    
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        
        with st.form("form_login"):
            
            try: 
                
                st.image("assets/logo.png", use_container_width=True) 
            except: 
                st.markdown("<h2 style='text-align: center; color: #004587; margin-bottom: 0;'>SENAI HUB</h2>", unsafe_allow_html=True)
            
            st.markdown("<p style='text-align: center; color: #666; font-size: 15px; margin-top: 0;'>Gestão de Salas • Acesso Restrito</p>", unsafe_allow_html=True)
            
            st.info("👋 Olá! Insira sua credencial para acessar o painel.")
            
            
            senha_input = st.text_input("Senha de Acesso", type="password", placeholder="Digite a senha...")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submit = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit:
                if "senha_coordenacao" in st.secrets:
                    senha_correta = st.secrets["senha_coordenacao"]
                    
                    if senha_input == senha_correta:
                        st.session_state['logado'] = True
                        st.rerun() 
                    else:
                        st.error("❌ Senha incorreta.")
                else:
                    st.error("⚠️ ERRO DE SISTEMA: Senha não configurada no cofre do servidor.")
    
    st.stop() 


with open("style/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# LISTAS DE DADOS

OPCOES_INICIO = ["07:30", "13:00", "13:30", "18:00", "18:30"]
OPCOES_FIM = ["11:00", "11:30", "16:00", "17:00", "17:30", "21:50"]

OPCOES_INTERVALO = [
    "Sem Intervalo", 
    "08:45 – 09:05",
    "09:10 – 09:30",
    "09:35 – 09:55",
    "14:45 – 15:05",
    "15:10 – 15:30",
    "15:35 – 15:55",
    "19:40 – 20:00",
    "20:05 – 20:25"
]

with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    try: st.image("assets/logo.png", use_container_width=True)
    except: pass
    st.markdown("---")
    try:
        st.image("assets/1.png", use_container_width=True)
        
    except: pass
    st.caption("Sistema de Gestão v1.0")


# HEADER

st.markdown("""
<div class="header-senai">
    <h1>Gestão de Salas</h1>
    <p>Painel de Controle de Ensalamento e Recursos</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Novo Agendamento", "Visualizar Agenda", "Coordenação", "Dashboard"])


# TAB 1: AGENDAMENTO 
 

with tab1:
    
    lista_docentes = carregar_lista_auxiliar("Docentes")
    lista_turmas = carregar_lista_auxiliar("Turmas")
    lista_salas = carregar_lista_auxiliar("Salas")

    with st.form("form_agendamento"):
        st.subheader("Dados do Agendamento")
        c1, c2 = st.columns(2)
        
        
        with c1:
            professor = st.selectbox("Docente", lista_docentes) if lista_docentes else st.text_input("Docente (Cadastre na aba Coordenação)")
            turma = st.selectbox("Turma/Curso", lista_turmas) if lista_turmas else st.text_input("Turma (Cadastre na aba Coordenação)")
            sala = st.selectbox("Ambiente / Sala", lista_salas) if lista_salas else st.warning("Cadastre salas na aba Coordenação")
            
            
            st.markdown("<br>", unsafe_allow_html=True) 
            data = st.date_input("Data da Aula")
            
            
            st.markdown("<br>", unsafe_allow_html=True)
            qtd_alunos = st.number_input("Quantidade de Alunos", min_value=0, step=1, help="Número aproximado de alunos")
        
        # --- COLUNA DA DIREITA (c2) ---
        with c2:
            turno = st.selectbox("Turno", ["Manhã", "Tarde", "Noite", "Integral"])
            situacao = st.radio("Período", ["Turno Inteiro", "1º Horário", "2º Horário"], horizontal=True)
            
            
            ch1, ch2 = st.columns(2)
            hora_inicio = ch1.selectbox("Início Aula", OPCOES_INICIO)
            hora_fim = ch2.selectbox("Fim Aula", OPCOES_FIM)
            
            
            st.markdown("<br>", unsafe_allow_html=True)
            ci1, ci2 = st.columns(2)
            with ci1:
                st.markdown(
                    """
                    <p style='margin-bottom: 7px; font-size: 14px; font-weight: bold;'>Intervalo</p>
                    """, 
                    unsafe_allow_html=True
                )
                sel_intervalo = st.selectbox("Selecione intervalo", OPCOES_INTERVALO, label_visibility="collapsed")
            
            
            if sel_intervalo and "–" in sel_intervalo:
                partes = sel_intervalo.split("–")
                inicio_intervalo = partes[0].strip()
                fim_intervalo = partes[1].strip()
            else:
                inicio_intervalo = ""
                fim_intervalo = ""

        st.markdown("---")
        st.markdown(f"**Recursos Móveis (Estoque: {TOTAL_CHROMEBOOKS} Chrome | {TOTAL_NOTEBOOKS} Note)**")
        cr1, cr2 = st.columns(2)
        qtd_chrome = cr1.number_input("Qtd. Chromebooks", 0, TOTAL_CHROMEBOOKS)
        qtd_note = cr2.number_input("Qtd. Notebooks", 0, TOTAL_NOTEBOOKS)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botão de confirmação
        if st.form_submit_button("Confirmar Agendamento", type="primary", use_container_width=True):
            
            if not professor or not turma or not sala:
                st.warning("⚠️ Verifique se Docente, Turma e Sala estão selecionados.")
            else:
                
                obj_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
                obj_fim = datetime.strptime(hora_fim, "%H:%M").time()
                
                
                if obj_fim <= obj_inicio:
                    st.error("❌ Erro de Lógica: O horário de FIM deve ser maior que o INÍCIO.")
                else:
                    df_check = carregar_dados()
                    conflito, msg_c = verificar_conflito_sala(df_check, sala, data, obj_inicio, obj_fim)
                    recurso_ok, msg_r = verificar_disponibilidade_recursos(df_check, data, obj_inicio, obj_fim, qtd_chrome, qtd_note)
                    
                    if conflito or not recurso_ok:
                        if conflito: st.error(f"❌ {msg_c}")
                        if not recurso_ok: 
                            with st.container(): st.error(f"❌ Indisponibilidade de Recursos:\n{msg_r}")
                    else:
                        ss = conectar_google_sheets()
                        sheet = ss.sheet1
                        
                        
                        sheet.append_row([
                            str(data), turno, situacao, hora_inicio, hora_fim,
                            str(sala).upper(),      
                            str(professor).upper(), 
                            str(turma).upper(),     
                            str(datetime.now()),
                            qtd_chrome, qtd_note, inicio_intervalo, fim_intervalo,
                            qtd_alunos              
                        ])
                        st.success("✅ Agendado com sucesso!")
                        import time
                        time.sleep(1.5)
                        st.rerun()


# TAB 2: VISUALIZAÇÃO (CORRIGIDA)

with tab2:
    
    c1, c2, c3 = st.columns([1,2,1])
    filtro_data = c1.date_input("Data", datetime.today())
    filtro_turno = c2.multiselect("Turno", ["Manhã", "Tarde", "Noite", "Integral"], default=["Manhã", "Tarde", "Noite", "Integral"])
    if c3.button("🔄 Atualizar"): st.cache_data.clear()

    df = carregar_dados()
    if not df.empty:
        df['data'] = df['data'].astype(str)
        
        df_view = df[(df['data'] == str(filtro_data)) & (df['turno'].isin(filtro_turno))].sort_values('hora_inicio')
        
        if not df_view.empty:
            
            df_view['intervalo_tela'] = df_view.apply(
                lambda r: f"{str(r['inicio_intervalo'])}-{str(r['fim_intervalo'])}" 
                if r['inicio_intervalo'] and str(r['inicio_intervalo']).strip() != "" 
                else "-", 
                axis=1
            )

            cols_view = ['hora_inicio', 'hora_fim', 'situacao', 'sala', 'professor', 'turma', 'qtd_alunos', 'intervalo_tela', 'qtd_chromebooks', 'qtd_notebooks']
            
            df_display = df_view[cols_view].rename(columns={
                'hora_inicio': 'Início',
                'hora_fim': 'Fim',
                'situacao': 'Situação',
                'sala': 'Ambiente',
                'professor': 'Professor',
                'turma': 'Turma',
                'qtd_alunos': 'Alunos',
                'intervalo_tela': 'Intervalo', 
                'qtd_chromebooks': 'Chromebooks',
                'qtd_notebooks': 'Notebooks'
            })
            
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Alunos": st.column_config.NumberColumn(
                        "Alunos",
                        format="%d", 
                    ),
                    "Chromebooks": st.column_config.NumberColumn(
                        "Chromebooks",
                        format="%d",
                    ),
                    "Notebooks": st.column_config.NumberColumn(
                        "Notebooks",
                        format="%d",
                    )
                }
            )
            
            
            col_d1, _ = st.columns([1,3])
            buf = gerar_imagem_ensalamento(df_view, filtro_data)
            col_d1.download_button("📥 Baixar Relatório (PNG)", data=buf, file_name=f"Ensalamento_{filtro_data}.png", mime="image/png")
            
            total_alunos = int(df_view['qtd_alunos'].sum())
            st.caption(f"Total Reservado: {df_view['qtd_chromebooks'].sum()} Chromebooks | {df_view['qtd_notebooks'].sum()} Notebooks | Total Alunos: {total_alunos}")
        else:
            st.info("Nenhum agendamento encontrado.")



# TAB 3: COORDENAÇÃO 

with tab3:
    st.subheader("Gestão de Cadastros e Agendamentos")
    
    with st.expander("Remover Agendamentos", expanded=True):
        st.warning("Cuidado: A exclusão é permanente.")
        
        col_del1, col_del2 = st.columns(2)
        data_del = col_del1.date_input("Filtrar Data", datetime.today(), key="data_del")
        turno_del = col_del2.selectbox("Filtrar Turno", ["Manhã", "Tarde", "Noite", "Integral"], key="turno_del")
        
        df_del = carregar_dados()
        
        if not df_del.empty:
            df_del['data'] = df_del['data'].astype(str)
            
            aulas_filtradas = df_del[
                (df_del['data'] == str(data_del)) & 
                (df_del['turno'] == turno_del)
            ]
            
            if not aulas_filtradas.empty:
                
                opcoes_exclusao = {
                    f"{row['sala']} | {row['professor']} | {row['hora_inicio']} - {row['hora_fim']}": i 
                    for i, row in aulas_filtradas.iterrows()
                }
                
                escolha_exclusao = st.selectbox("Selecione o agendamento para EXCLUIR:", list(opcoes_exclusao.keys()))
                
                if st.button("❌ Confirmar Exclusão"):
                    try:
                        ss = conectar_google_sheets()
                        ws = ss.sheet1
                        
                        idx_df = opcoes_exclusao[escolha_exclusao]
                        linha_dados = aulas_filtradas.loc[idx_df]
                        
                        todos_dados = ws.get_all_records()
                        linha_para_deletar = None
                        
                        for i, registro in enumerate(todos_dados):
                            if (str(registro['data']) == str(linha_dados['data']) and 
                                registro['sala'] == linha_dados['sala'] and 
                                registro['hora_inicio'] == linha_dados['hora_inicio'] and
                                registro['professor'] == linha_dados['professor']):
                                
                                linha_para_deletar = i + 2 
                                break
                        
                        if linha_para_deletar:
                            ws.delete_rows(linha_para_deletar)
                            st.success(f"Agendamento removido com sucesso!")
                            
                            import time; time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("Erro ao localizar a linha na planilha. Tente atualizar a página.")
                            
                    except Exception as e:
                        st.error(f"Erro de conexão ao excluir: {e}")
            else:
                st.info("Nenhum agendamento encontrado para esta Data/Turno.")
        else:
            st.info("Banco de dados vazio.")

    st.markdown("---")
    st.info("Utilize esta área para alimentar as listas do sistema.")
    
    col_a, col_b, col_c = st.columns(3)
    
    # --- CADASTRO DE DOCENTES ---
    with col_a:
        st.markdown("**🧑‍🏫 Docentes**")
        with st.form("add_docente", clear_on_submit=True):
            novo_docente = st.text_input("Nome do Docente")
            if st.form_submit_button("Adicionar"):
                if novo_docente:
                    ss = conectar_google_sheets()
                    try:
                        ws = ss.worksheet("Docentes")
                        ws.append_row([novo_docente])
                        st.success("Docente salvo com sucesso!")
                        # CORREÇÃO AQUI: Limpa SÓ a lista auxiliar
                        carregar_lista_auxiliar.clear()
                        import time; time.sleep(1.5)
                        st.rerun() 
                    except: st.error("Aba 'Docentes' não encontrada.")
    
    # --- CADASTRO DE TURMAS ---
    with col_b:
        st.markdown("**🎓 Turmas**")
        with st.form("add_turma", clear_on_submit=True):
            nova_turma = st.text_input("Nome da Turma")
            if st.form_submit_button("Adicionar"):
                if nova_turma:
                    ss = conectar_google_sheets()
                    try:
                        ws = ss.worksheet("Turmas")
                        ws.append_row([nova_turma])
                        st.success("Turma salva com sucesso!")
                        # CORREÇÃO AQUI
                        carregar_lista_auxiliar.clear()
                        import time; time.sleep(1.5)
                        st.rerun()
                    except: st.error("Aba 'Turmas' não encontrada.")

    # --- CADASTRO DE SALAS ---
    with col_c:
        st.markdown("**🏫 Ambientes**")
        with st.form("add_sala", clear_on_submit=True):
            nova_sala = st.text_input("Nome da Sala")
            if st.form_submit_button("Adicionar"):
                if nova_sala:
                    ss = conectar_google_sheets()
                    try:
                        ws = ss.worksheet("Salas")
                        ws.append_row([nova_sala])
                        st.success("Sala salva com sucesso!")
                        # CORREÇÃO AQUI
                        carregar_lista_auxiliar.clear()
                        import time; time.sleep(1.5)
                        st.rerun()
                    except: st.error("Aba 'Salas' não encontrada.")
    
    st.markdown("---")
    
    if st.checkbox("Visualizar listas cadastradas"):
        ld = carregar_lista_auxiliar("Docentes")
        lt = carregar_lista_auxiliar("Turmas")
        ls = carregar_lista_auxiliar("Salas")
        c1, c2, c3 = st.columns(3)
        c1.write(ld); c2.write(lt); c3.write(ls)

# TAB 4: DASHBOARD INTERATIVO

with tab4:
    st.markdown("<br>", unsafe_allow_html=True)
    c_dash1, c_dash2, c_dash3 = st.columns([1, 2, 1])
    
    # Filtro de data centralizado
    data_dash = c_dash2.date_input("📅 Selecione a Data para Análise", datetime.today(), key="data_dash")
    
    df_dash = carregar_dados()
    
    if not df_dash.empty:
        df_dash['data'] = df_dash['data'].astype(str)
        df_dia = df_dash[df_dash['data'] == str(data_dash)]
        
        if not df_dia.empty:
            st.markdown("---")
            
            # --- 1. INDICADORES (KPIs) ---
            kpi1, kpi2, kpi3 = st.columns(3)
            total_alunos = int(df_dia['qtd_alunos'].sum())
            uso_chrome = int(df_dia['qtd_chromebooks'].sum())
            uso_note = int(df_dia['qtd_notebooks'].sum())
            
            kpi1.metric("👥 Total de Alunos Atendidos", total_alunos)
            kpi2.metric("💻 Chromebooks Reservados", f"{uso_chrome} / {TOTAL_CHROMEBOOKS}")
            kpi3.metric("🖥️ Notebooks Reservados", f"{uso_note} / {TOTAL_NOTEBOOKS}")
            
            st.markdown("<br><br>", unsafe_allow_html=True)
            
            # --- 2. GRÁFICOS INTERATIVOS ---
            col_graf1, col_graf2 = st.columns(2)
            
            with col_graf1:
                # Gráfico de Barras: Uso por Ambiente
                uso_salas = df_dia['sala'].value_counts().reset_index()
                uso_salas.columns = ['Ambiente', 'Reservas']
                
                fig_salas = px.bar(
                    uso_salas, x='Ambiente', y='Reservas', 
                    title="Ambientes Mais Utilizados",
                    color='Reservas', 
                    color_continuous_scale='Blues' # Usa paleta de azul SENAI
                )
                # Oculta fundo para ficar clean no modo escuro
                fig_salas.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)") 
                st.plotly_chart(fig_salas, use_container_width=True)

            with col_graf2:
                # Gráfico de Rosca: Alunos por Turno
                alunos_turno = df_dia.groupby('turno')['qtd_alunos'].sum().reset_index()
                
                fig_turnos = px.pie(
                    alunos_turno, names='turno', values='qtd_alunos', 
                    title="Distribuição de Alunos por Turno",
                    hole=0.4, # Deixa com formato de rosca (Donut)
                    color_discrete_sequence=['#2b78c5', '#e94d16', '#198754', '#ffc107']
                )
                fig_turnos.update_layout(paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_turnos, use_container_width=True)
                
        else:
            st.info("Nenhum agendamento registrado para esta data. Os gráficos aparecerão aqui quando houver reservas.")
    else:
        st.info("O banco de dados está vazio.")