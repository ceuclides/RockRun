import gspread
from google.oauth2.service_account import Credentials
import datetime

def conectar_google_sheets():
    """Conecta ao Google Sheets API"""
    try:
        # Escopos necessários
        escopos = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Tenta usar as credenciais do Streamlit (secrets)
        try:
            from streamlit import secrets
            credenciais = Credentials.from_service_account_info(
                secrets["gcp_service_account"],
                scopes=escopos
            )
        except:
            # Fallback para arquivo local (em desenvolvimento)
            CREDENTIALS_PATH = 'credentials.json'
            credenciais = Credentials.from_service_account_file(
                CREDENTIALS_PATH, 
                scopes=escopos
            )
        
        cliente = gspread.authorize(credenciais)
        return cliente, None  # Sucesso: retorna cliente e None para erro
    
    except Exception as e:
        return None, f"🚨 Erro na conexão: {str(e)}"  # Falha: retorna None e mensagem de erro

def salvar_dados_sheets(respostas, classificacao):
    """Salva os dados na planilha do Google Sheets"""
    try:
        cliente, erro = conectar_google_sheets()
        if erro or not cliente:
            return False, erro or "Falha desconhecida na conexão"
        
        # ID da planilha
        SHEET_ID = "1WdcJclPYrrLoBJfIRrNLd9WEVJ9v2Rh5bekmwlAGjb0"
        
        # Abre a planilha
        planilha = cliente.open_by_key(SHEET_ID)
        
        # Seleciona a primeira aba
        folha = planilha.sheet1
        
        # Cabeçalhos
        cabecalhos = [
            "Timestamp", "Nome", "Telefone", "Perfil", "Objetivo", 
            "Idade", "Sexo", "Condicao_Fisica", "Dias_Semana", 
            "Tempo_Treino", "Horario", "Local", "Lesoes"
        ]
        
        # Verifica se precisa adicionar cabeçalhos
        if not folha.get_all_values():
            folha.append_row(cabecalhos)
        
        # Prepara os dados
        dados = [
            datetime.datetime.now().strftime("%d/%m/%Y %H:%M"),  # Timestamp
            respostas.get('nome', ''),
            respostas.get('telefone', ''),
            classificacao,
            respostas.get('objetivo', ''),
            respostas.get('idade', ''),
            respostas.get('sexo', ''),
            str(respostas.get('condicao_fisica', '')),  # Converte para string
            respostas.get('dias_semana', ''),
            respostas.get('tempo_treino', ''),
            respostas.get('horario', ''),
            respostas.get('local', ''),
            respostas.get('lesoes', '')
        ]
        
        # Adiciona nova linha
        folha.append_row(dados)
        return True, ""  # Sucesso sem mensagem de erro
        
    except gspread.exceptions.APIError as e:
        error_msg = e.response.json().get('error', {}).get('message', str(e))
        return False, f"🚨 Erro API Google: {error_msg}"
        
    except Exception as e:
        return False, f"🚨 Erro geral: {str(e)}"