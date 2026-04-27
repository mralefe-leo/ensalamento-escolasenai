from datetime import datetime

# CONSTANTES DE ESTOQUE
TOTAL_CHROMEBOOKS = 34
TOTAL_NOTEBOOKS = 11

def verificar_conflito_sala(df, sala, data_agendamento, inicio_novo, fim_novo):
    if df.empty: return False, ""
    
    df['data'] = df['data'].astype(str).str.strip()
    df['sala_norm'] = df['sala'].astype(str).str.strip().str.upper()
    sala_check = str(sala).strip().upper()
    
    conflitos = df[
        (df['sala_norm'] == sala_check) & 
        (df['data'] == str(data_agendamento))
    ]
    
    for _, row in conflitos.iterrows():
        try:
            str_ini = str(row['hora_inicio']).strip()
            str_fim = str(row['hora_fim']).strip()
            
            if len(str_ini) > 5: str_ini = str_ini[:5]
            if len(str_fim) > 5: str_fim = str_fim[:5]

            ini_exist = datetime.strptime(str_ini, "%H:%M").time()
            fim_exist = datetime.strptime(str_fim, "%H:%M").time()
            
            if (inicio_novo < fim_exist) and (fim_novo > ini_exist):
                return True, f"Sala ocupada por {row['professor']} ({str_ini}-{str_fim})"
        except: 
            continue
            
    return False, ""

def verificar_disponibilidade_recursos(df, data_agendamento, inicio_novo, fim_novo, qtd_chrome, qtd_note):
    if qtd_chrome == 0 and qtd_note == 0: return True, ""
    if df.empty: return True, ""
    
    df['data'] = df['data'].astype(str)
    agendamentos = df[df['data'] == str(data_agendamento)]
    chrome_uso, note_uso = 0, 0
    
    for _, row in agendamentos.iterrows():
        try:
            str_ini, str_fim = str(row['hora_inicio'])[:5], str(row['hora_fim'])[:5]
            ini_exist = datetime.strptime(str_ini, "%H:%M").time()
            fim_exist = datetime.strptime(str_fim, "%H:%M").time()
            
            if (inicio_novo < fim_exist) and (fim_novo > ini_exist):
                chrome_uso += int(row['qtd_chromebooks'])
                note_uso += int(row['qtd_notebooks'])
        except: continue
    
    erros_estoque = []
    
    saldo_chrome = TOTAL_CHROMEBOOKS - chrome_uso
    if qtd_chrome > saldo_chrome:
        erros_estoque.append(f"- Chromebooks: Pedido {qtd_chrome} | Disponível: {saldo_chrome}")
        
    saldo_note = TOTAL_NOTEBOOKS - note_uso
    if qtd_note > saldo_note:
        erros_estoque.append(f"- Notebooks: Pedido {qtd_note} | Disponível: {saldo_note}")
        
    if len(erros_estoque) > 0:
        return False, "\n".join(erros_estoque)
        
    return True, ""