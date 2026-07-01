import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

@st.cache_resource
def conectar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = None
    
    if "gcp_service_account" in st.secrets:
        try:
            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict: 
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except: pass
    
    if not creds:
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        except: 
            st.error("Erro de credenciais")
            st.stop()
    
    return gspread.authorize(creds).open("sistema_ensalamento_db_unidade2")

def carregar_dados():
    try:
        sheet = conectar_google_sheets().sheet1
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        if not df.empty: df.columns = df.columns.str.lower().str.strip()
        
        colunas = ['data', 'turno', 'situacao', 'hora_inicio', 'hora_fim', 'sala', 'professor', 'turma', 'data_registro', 'qtd_chromebooks', 'qtd_notebooks', 'inicio_intervalo', 'fim_intervalo', 'qtd_alunos']
        
        if df.empty: return pd.DataFrame(columns=colunas)
        
        for col in colunas:
            if col not in df.columns: df[col] = 0 if 'qtd' in col else ''
            
        df['qtd_chromebooks'] = pd.to_numeric(df['qtd_chromebooks'], errors='coerce').fillna(0).astype(int)
        df['qtd_notebooks'] = pd.to_numeric(df['qtd_notebooks'], errors='coerce').fillna(0).astype(int)
        df['qtd_alunos'] = pd.to_numeric(df['qtd_alunos'], errors='coerce').fillna(0).astype(int)
        
        return df
    except: return pd.DataFrame()

@st.cache_data(ttl=600)
def carregar_lista_auxiliar(nome_aba):
    try:
        ss = conectar_google_sheets()
        worksheet = ss.worksheet(nome_aba)
        valores = worksheet.col_values(1)
        if valores:
            return sorted(valores[1:]) 
        return []
    except: return []

