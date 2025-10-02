# Importações do sistema
import os
import sys
import io
import datetime
import traceback

# Adiciona o diretório src ao path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Streamlit e visualização
import streamlit as st
import pandas as pd
import numpy as np

# Nossos módulos
from utils.helpers import formatar_tel
from utils.gsheets import conectar_google_sheets, salvar_dados_sheets
from utils.pdf_generator import gerar_pdf
from utils.training_logic import (
    calcular_classificacao,
    identificar_restricoes,
    gerar_programa_treino,
    adaptar_por_objetivo,
    gerar_exercicios_complementares
)

def main():
    # CSS personalizado com novo design
    st.markdown("""
    <style>
        /* Definição de variáveis de cor para reutilização no tema */
        :root {
            --primary: #FF6B35;      /* Cor principal (laranja) */
            --secondary: #2E86AB;    /* Cor secundária (azul) */
            --accent: #4CAF50;       /* Cor de destaque (verde água) */
            --dark: #292F36;         /* Cor escura (quase preto) */
            --light: #F7F9FC;        /* Cor clara (quase branco) */
            --success: #4CAF50;      /* Verde para sucesso */
            --warning: #FF9800;      /* Laranja para alerta */
            --danger: #F44336;       /* Vermelho para erro */
        }
        
        /* Estilo do cabeçalho principal */
        .main-header {
            
            text-align: left; /* Alinha o texto à esquerda */
            color: #22F20F; /* Usa a cor principal (mas é sobrescrita pelo gradiente) */
            font-size: 2.5rem; /* Tamanho grande da fonte */
            font-weight: 800; /* Negrito forte */
            margin-bottom: 1rem; /* Espaço abaixo */
            text-shadow: 1px 1px 3px rgba(0,0,0,0.1); /* Sombra leve no texto */
            background: linear-gradient(45deg, white, #22F20F); /* Gradiente no texto */
            -webkit-background-clip: text; /* Aplica o gradiente só no texto */
            -webkit-text-fill-color: transparent; /* Torna o texto transparente para mostrar o gradiente */
            padding: 0.5rem 0; /* Espaçamento vertical interno */
        }
        
        /* Estilo do cabeçalho de seção */
        .section-header {
            color: var(--secondary); /* Cor secundária */
            font-size: 1.5rem; /* Tamanho médio da fonte */
            font-weight: 700; /* Negrito */
            margin-top: 2rem; /* Espaço acima */
            margin-bottom: 1rem; /* Espaço abaixo */
            padding-bottom: 0.5rem; /* Espaço interno abaixo */
            border-bottom: 2px solid var(--secondary); /* Linha inferior */
            position: relative; /* Necessário para o ::after */
        }
        
        /* Linha de destaque abaixo do cabeçalho de seção */
        .section-header::after {
            content: ""; /* Elemento vazio */
            position: absolute; /* Posicionamento absoluto */
            bottom: -2px; /* 2px abaixo do fundo */
            left: 0; /* Alinhado à esquerda */
            width: 50px; /* Largura da linha */
            height: 4px; /* Altura da linha */
            background: var(--accent); /* Cor de destaque */
        }
        
        /* Estilo dos botões do Streamlit */
        .stButton > button {
            width: 100%; /* Ocupa toda a largura */
            background: linear-gradient(135deg, var(--primary), var(--accent)); /* Gradiente */
            color: white; /* Texto branco */
            font-weight: bold; /* Negrito */
            font-size: 1.1rem; /* Tamanho da fonte */
            height: 3rem; /* Altura fixa */
            border-radius: 12px; /* Cantos arredondados */
            border: none; /* Sem borda */
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* Sombra */
            transition: all 0.3s ease; /* Transição suave */
        }
        
        /* Efeito ao passar o mouse no botão */
        .stButton > button:hover {
            transform: translateY(-2px); /* Sobe levemente */
             box-shadow: 0 6px 8px rgba(0,0,0,0.15); /* Sombra mais forte */
        }
        
        /* Efeito ao clicar no botão */
        .stButton > button:active {
            transform: translateY(0); /* Volta ao normal */
        }
        
        /* Caixa de sucesso (mensagens positivas) */
        .success-box {
            background: linear-gradient(135deg, #d4edda, #c3e6cb); /* Gradiente verde claro */
            border-radius: 12px; /* Cantos arredondados */
            padding: 1.5rem; /* Espaço interno */
            margin: 1.5rem 0; /* Espaço externo */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); /* Sombra leve */
            border-left: 5px solid var(--success); /* Barra verde à esquerda */
        }
        
        /* Adiciona asterisco vermelho em campos obrigatórios */
        .required::after {
            content: " *"; /* Asterisco */
            color: var(--danger); /* Vermelho */
            font-weight: bold; /* Negrito */
        }
        
        /* Container da barra de progresso */
        .progress-container {
            margin: 1.5rem 0; /* Espaço externo */
            padding: 1rem; /* Espaço interno */
            border-radius: 12px; /* Cantos arredondados */
            background: var(--light); /* Fundo claro */
            border: 1px solid #e0e0e0; /* Borda cinza clara */
            box-shadow: 0 4px 6px rgba(0,0,0,0.05); /* Sombra leve */
        }
        
        /* Botões de navegação em etapas */
        .step-buttons {
            display: flex; /* Layout flexível */
            justify-content: space-between; /* Espaço entre botões */
            margin-top: 1.5rem; /* Espaço acima */
            gap: 0.5rem; /* Espaço entre botões */
        }
        
        /* Barra de progresso customizada */
        .stProgress > div > div > div {
            background: linear-gradient(100deg, white, #22F20F); /* Gradiente */
            border-radius: 10px; /* Cantos arredondados */
        }
        
        /* Mensagem de erro */
        .error-message {
            color: var(--danger); /* Vermelho */
            font-weight: bold; /* Negrito */
            margin-top: 0.5rem; /* Espaço acima */
            padding: 0.75rem; /* Espaço interno */
            border-radius: 8px; /* Cantos arredondados */
            background-color: #ffebee; /* Fundo vermelho claro */
            border-left: 4px solid var(--danger); /* Barra vermelha à esquerda */
        }
        
        /* Cartão de conteúdo */
        .card {
            background: white; /* Fundo branco */
            border-radius: 12px; /* Cantos arredondados */
            padding: 1.5rem; /* Espaço interno */
            margin: 1rem 0; /* Espaço externo */
            box-shadow: 0 4px 12px rgba(0,0,0,0.08); /* Sombra */
            border: 1px solid #eaeaea; /* Borda cinza clara */
            transition: all 0.3s ease; /* Transição suave */
        }
        
        /* Efeito ao passar o mouse no cartão */
        .card:hover {
            transform: translateY(-3px); /* Sobe levemente */
            cursor: pointer; /* Muda o cursor */
            box-shadow: 0 6px 16px rgba(0,0,0,0.12); /* Sombra mais forte */
        }
        
        /* Sidebar do Streamlit */
        [data-testid="stSidebar"] {
            background: linear-gradient(100deg, #81EB78, #81EB78); /* Gradiente verde-escuro */
            color: white; /* Texto branco */
        }
        
        /* Remove fundo de alguns elementos do sidebar */
        [data-testid="stSidebar"] .st-bb {
            background-color: transparent;
        }
        [data-testid="stSidebar"] .st-cb {
            background-color: rgba(255,255,255,0.1);
        }
        
        /* Deixa todos os textos do sidebar brancos */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] h4, 
        [data-testid="stSidebar"] h5, 
        [data-testid="stSidebar"] h6,
        [data-testid="stSidebar"] p {
            color: #292F36 !important;
        }
        
        /* Responsividade para telas pequenas (mobile) */
        @media (max-width: 768px) {
            .main-header {
                font-size: 1.8rem; /* Reduz tamanho do título */
            }
            .section-header {
                font-size: 1.3rem; /* Reduz tamanho do subtítulo */
            }
            .step-buttons {
                flex-direction: column; /* Botões em coluna */
            }
        }
        
        /* Estilo para container de botões de navegação */
        .nav-buttons-container {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            margin-top: 1.5rem;
        }
        .full-width-button {
            width: 100%;
            margin-top: 1rem;
        }
                

        /* ESTILO DOS BOTÕES PRINCIPAIS (mantenha como está) */
        .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        height: 3rem;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    /* === NOVOS ESTILOS PARA BOTÕES DE NAVEGAÇÃO === */
    .nav-buttons .stButton > button {
        background-color: #81EB78 !important;
        color: #292F36 !important;
        border: 2px solid transparent !important;
        transition: all 0.3s ease !important;
    }

    .nav-buttons .stButton > button:hover {
        background-color: transparent !important;
        border: 2px solid #81EB78 !important;
        color: #81EB78 !important;
    }

    .nav-buttons .stButton > button:active {
        background-color: #22F20F !important;
        color: white !important;
        border: 2px solid transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Cabeçalho moderno
    #st.markdown(("---"))
    st.markdown('<h2 class="main-header">RockRun - Seu Personal de Corrida!</h2>', unsafe_allow_html=True)
    st.markdown(("---"))
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.0rem; color: var(--light);">Descubra seu perfil e receba um plano de treino personalizado baseado em ciência esportiva!</p>
        <div style="display: flex; justify-content: center; gap: 1rem; margin-top: 1rem;">
            <span style="background: #AEE7CC; color: #292F36; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">✅ Personalizado</span>
            <span style="background: #AEE7CC; color: #292F36; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">📊 Base Científica</span>
            <span style="background: #AEE7CC; color: #292F36; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.9rem;">💯 Gratuito</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Inicializar session state
    if 'respostas' not in st.session_state:
        st.session_state.respostas = {}
    if 'form_valido' not in st.session_state:
        st.session_state.form_valido = False
    if 'etapa_formulario' not in st.session_state:
        st.session_state.etapa_formulario = 0
    if 'erros_etapa1' not in st.session_state:
        st.session_state.erros_etapa1 = []

    # Inicializar todas as variáveis do formulário
    nome = telefone_input = idade = sexo = ""
    inatividade = experiencia = ""
    saude = medicamentos = liberacao_medica = ""
    condicao_fisica = escada = caminhada = 0
    objetivo = motivacao = ""
    dias_semana = tempo_treino = horario = local = ""
    sono = estresse = 0
    lesoes = preferencia_social = ""

    # Sidebar atualizada
    st.sidebar.header("⚙️ Configurações do Sistema")
    st.sidebar.subheader("🔍 Diagnóstico de Conexão")
    
    # Verifica se o arquivo credentials.json existe
    CREDENTIALS_PATH = 'credentials.json'
    credentials_exist = os.path.exists(CREDENTIALS_PATH)
    
    st.sidebar.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <p style="margin-bottom: 0.5rem;"><strong>🔑 Credenciais:</strong> {'✅ Encontradas' if credentials_exist else '❌ Não encontradas'}</p>
        <p style="font-size: 0.8rem; margin-bottom: 0;">{'Excluir depois' if credentials_exist else 'Coloque na pasta do app'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botão para testar conexão
    if st.sidebar.button("🧪 Testar Conexão Google Sheets", use_container_width=True):
        cliente, erro = conectar_google_sheets()
        if erro:
            st.sidebar.error(f"❌ {erro}")
        elif cliente:
            try:
                planilha = cliente.open_by_key("1WdcJclPYrrLoBJfIRrNLd9WEVJ9v2Rh5bekmwlAGjb0")
                st.sidebar.success("✅ Conexão bem-sucedida!")
                st.sidebar.info(f"📊 Planilha: {planilha.title}")
            except Exception as e:
                st.sidebar.error(f"❌ Falha: {str(e)}")
        else:
            st.sidebar.error("❌ Conexão falhou sem mensagem de erro")
    
    # Informações sobre o app
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ℹ️ Sobre o RockRun")
    st.sidebar.markdown("Plataforma para corredores amadores criarem planos de treino personalizados com base científica.")
    st.sidebar.markdown("Desenvolvido com ❤️ usando Python e Streamlit")
    st.sidebar.caption("Versão 1.0.1 | Junho 2025")
    st.sidebar.markdown("© 2025 RockRun. Todos os direitos reservados.")

    # Lista de etapas do formulário
    ETAPAS = [
        "DADOS PESSOAIS", #👤
        "📚 HISTÓRICO DE ATIVIDADES FÍSICAS",
        "🏥 CONDIÇÃO DE SAÚDE",
        "💪 CONDICIONAMENTO FÍSICO ATUAL",
        "🎯 OBJETIVOS E MOTIVAÇÃO",
        "⏰ DISPONIBILIDADE",
        "🌟 ESTILO DE VIDA"
    ]
    
    # Barra de progresso moderna
    with st.container():
        progresso = st.session_state.etapa_formulario / (len(ETAPAS) - 1)
        st.progress(progresso)
        
        icons = ["", "📚", "🏥", "💪", "🎯", "⏰", "🌟"]
        current_icon = icons[st.session_state.etapa_formulario]
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
            <div style="font-weight: 300; font-size: 0.8rem; color: #666;">
                Etapa {st.session_state.etapa_formulario + 1} de {len(ETAPAS)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Formulário multi-etapas em cartões
    form = st.form(key="formulario_corrida")
    with form:
        # ETAPA 0: Dados Pessoais
        if st.session_state.etapa_formulario == 0:
            with st.container():
                st.subheader("DADOS PESSOAIS")
                
                # Nome (campo obrigatório)
                nome = st.text_input("Digite seu nome*:", value=st.session_state.respostas.get('nome', ''))
                
                # Telefone (campo obrigatório com validação)
                telefone_input = st.text_input(
                    "Telefone* (formato: (99) 99999-9999):", 
                    value=st.session_state.respostas.get('telefone_input', ''),
                    placeholder="(99) 99999-9999",
                    max_chars=15
                )
                
                # Mostrar erros se existirem
                if st.session_state.erros_etapa1:
                    for erro in st.session_state.erros_etapa1:
                        st.markdown(f'<div class="error-message">{erro}</div>', unsafe_allow_html=True)
                
                idade = st.selectbox(
                    "1. Qual é a sua idade?",
                    ["Menos de 18 anos", "18-25 anos", "26-35 anos", "36-45 anos", "46-55 anos", "Mais de 55 anos"],
                    index=0 if 'idade' not in st.session_state.respostas else 
                    ["Menos de 18 anos", "18-25 anos", "26-35 anos", "36-45 anos", "46-55 anos", "Mais de 55 anos"].index(st.session_state.respostas['idade'])
                )
                sexo = st.selectbox(
                    "2. Qual é o seu sexo?",
                    ["Feminino", "Masculino", "Prefiro não informar"],
                    index=0 if 'sexo' not in st.session_state.respostas else 
                    ["Feminino", "Masculino", "Prefiro não informar"].index(st.session_state.respostas['sexo'])
                )
        
        # ETAPA 1: Histórico de Atividades Físicas
        elif st.session_state.etapa_formulario == 1:
            with st.container():
                st.subheader("📚 HISTÓRICO DE ATIVIDADES FÍSICAS")
                inatividade = st.selectbox(
                    "3. Há quanto tempo você não pratica exercícios físicos regulares?",
                    [
                        "Pratico atualmente (pelo menos 2x por semana)",
                        "Parei há menos de 6 meses",
                        "Parei há 6 meses a 1 ano",
                        "Parei há 1 a 3 anos",
                        "Parei há mais de 3 anos",
                        "Nunca pratiquei exercícios regulares"
                    ],
                    index=0 if 'inatividade' not in st.session_state.respostas else 
                    ["Pratico atualmente (pelo menos 2x por semana)",
                     "Parei há menos de 6 meses",
                     "Parei há 6 meses a 1 ano",
                     "Parei há 1 a 3 anos",
                     "Parei há mais de 3 anos",
                     "Nunca pratiquei exercícios regulares"].index(st.session_state.respostas['inatividade'])
                )
                
                experiencia = st.selectbox(
                    "4. Qual foi sua última experiência com atividade física regular?",
                    [
                        "Corrida/caminhada",
                        "Academia/musculação",
                        "Esportes coletivos (futebol, vôlei, etc.)",
                        "Dança ou lutas",
                        "Ciclismo ou natação",
                        "Nunca tive experiência regular"
                    ],
                    index=0 if 'experiencia' not in st.session_state.respostas else 
                    ["Corrida/caminhada",
                     "Academia/musculação",
                     "Esportes coletivos (futebol, vôlei, etc.)",
                     "Dança ou lutas",
                     "Ciclismo ou natação",
                     "Nunca tive experiência regular"].index(st.session_state.respostas['experiencia'])
                )
        
        # ETAPA 2: Condição de Saúde
        elif st.session_state.etapa_formulario == 2:
            with st.container():
                st.subheader("🏥 CONDIÇÃO DE SAÚDE")
                saude = st.selectbox(
                    "5. Você possui alguma condição de saúde que pode afetar a prática de exercícios?",
                    [
                        "Não tenho nenhuma condição",
                        "Problemas cardíacos",
                        "Diabetes",
                        "Hipertensão",
                        "Problemas respiratórios (asma, etc.)",
                        "Outras condições"
                    ],
                    index=0 if 'saude' not in st.session_state.respostas else 
                    ["Não tenho nenhuma condição",
                     "Problemas cardíacos",
                     "Diabetes",
                     "Hipertensão",
                     "Problemas respiratórios (asma, etc.)",
                     "Outras condições"].index(st.session_state.respostas['saude'])
                )
                
                medicamentos = st.selectbox(
                    "6. Você toma algum medicamento regularmente?",
                    [
                        "Não tomo medicamentos",
                        "Sim, mas não afeta exercícios",
                        "Sim, e pode afetar exercícios",
                        "Não tenho certeza"
                    ],
                    index=0 if 'medicamentos' not in st.session_state.respostas else 
                    ["Não tomo medicamentos",
                     "Sim, mas não afeta exercícios",
                     "Sim, e pode afetar exercícios",
                     "Não tenho certeza"].index(st.session_state.respostas['medicamentos'])
                )
                
                liberacao_medica = st.selectbox(
                    "7. Você tem liberação médica para praticar exercícios?",
                    [
                        "Sim, tenho liberação",
                        "Não preciso (sou saudável)",
                        "Pretendo consultar um médico antes",
                        "Não sei se preciso"
                    ],
                    index=0 if 'liberacao_medica' not in st.session_state.respostas else 
                    ["Sim, tenho liberação",
                     "Não preciso (sou saudável)",
                     "Pretendo consultar um médico antes",
                     "Não sei se preciso"].index(st.session_state.respostas['liberacao_medica'])
                )
        
        # ETAPA 3: Condicionamento Físico Atual
        elif st.session_state.etapa_formulario == 3:
            with st.container():
                st.subheader("💪 CONDICIONAMENTO FÍSICO ATUAL")
                condicao_fisica = st.slider(
                    "8. Como você avalia sua condição física atual?",
                    min_value=1, max_value=5, 
                    value=st.session_state.respostas.get('condicao_fisica', 3),
                    help="1 = Muito ruim, 5 = Excelente"
                )
                
                escada = st.selectbox(
                    "9. Você consegue subir 2 lances de escada sem ficar muito ofegante?",
                    [
                        "Sim, facilmente",
                        "Sim, mas fico um pouco cansado(a)",
                        "Com dificuldade",
                        "Não consigo"
                    ],
                    index=0 if 'escada' not in st.session_state.respostas else 
                    ["Sim, facilmente",
                     "Sim, mas fico um pouco cansado(a)",
                     "Com dificuldade",
                     "Não consigo"].index(st.session_state.respostas['escada'])
                )
                
                caminhada = st.selectbox(
                    "10. Quanto tempo você consegue caminhar em ritmo moderado sem parar?",
                    [
                        "Menos de 10 minutos",
                        "10-20 minutos",
                        "20-30 minutos",
                        "30-45 minutos",
                        "Mais de 45 minutos"
                    ],
                    index=0 if 'caminhada' not in st.session_state.respostas else 
                    ["Menos de 10 minutos",
                     "10-20 minutos",
                     "20-30 minutos",
                     "30-45 minutos",
                     "Mais de 45 minutos"].index(st.session_state.respostas['caminhada'])
                )
        
        # ETAPA 4: Objetivos e Motivação
        elif st.session_state.etapa_formulario == 4:
            with st.container():
                st.subheader("🎯 OBJETIVOS E MOTIVAÇÃO")
                objetivo = st.selectbox(
                    "11. Qual é seu principal objetivo com a corrida?",
                    [
                        "Emagrecimento/perda de peso",
                        "Melhorar a saúde geral",
                        "Reduzir estresse/bem-estar mental",
                        "Participar de provas/competições",
                        "Diversão e lazer",
                        "Socialização/fazer novos amigos"
                    ],
                    index=0 if 'objetivo' not in st.session_state.respostas else 
                    ["Emagrecimento/perda de peso",
                     "Melhorar a saúde geral",
                     "Reduzir estresse/bem-estar mental",
                     "Participar de provas/competições",
                     "Diversão e lazer",
                     "Socialização/fazer novos amigos"].index(st.session_state.respostas['objetivo'])
                )
                
                motivacao = st.slider(
                    "12. Qual é seu nível de motivação para começar?",
                    min_value=1, max_value=5, 
                    value=st.session_state.respostas.get('motivacao', 4),
                    help="1 = Pouco motivado, 5 = Muito motivado"
                )
        
        # ETAPA 5: Disponibilidade
        elif st.session_state.etapa_formulario == 5:
            with st.container():
                st.subheader("⏰ DISPONIBILIDADE")
                dias_semana = st.selectbox(
                    "13. Quantos dias por semana você pode treinar?",
                    ["1-2 dias", "3 dias", "4 dias", "5 dias", "6-7 dias"],
                    index=0 if 'dias_semana' not in st.session_state.respostas else 
                    ["1-2 dias", "3 dias", "4 dias", "5 dias", "6-7 dias"].index(st.session_state.respostas['dias_semana'])
                )
                
                tempo_treino = st.selectbox(
                    "14. Tempo disponível por sessão?",
                    [
                        "Menos de 20 minutos",
                        "20-30 minutos",
                        "30-45 minutos",
                        "45-60 minutos",
                        "Mais de 60 minutos"
                    ],
                    index=0 if 'tempo_treino' not in st.session_state.respostas else 
                    ["Menos de 20 minutos",
                     "20-30 minutos",
                     "30-45 minutos",
                     "45-60 minutos",
                     "Mais de 60 minutos"].index(st.session_state.respostas['tempo_treino'])
                )
                
                horario = st.selectbox(
                    "15. Horário preferido?",
                    [
                        "Manhã (6h às 9h)",
                        "Meio do dia (9h às 14h)",
                        "Tarde (14h às 18h)",
                        "Noite (18h às 21h)",
                        "Varia conforme o dia"
                    ],
                    index=0 if 'horario' not in st.session_state.respostas else 
                    ["Manhã (6h às 9h)",
                     "Meio do dia (9h às 14h)",
                     "Tarde (14h às 18h)",
                     "Noite (18h às 21h)",
                     "Varia conforme o dia"].index(st.session_state.respostas['horario'])
                )
                
                local = st.selectbox(
                    "16. Onde você prefere correr?",
                    [
                        "Rua/calçada",
                        "Parques/praças",
                        "Esteira (academia ou casa)",
                        "Pista de atletismo",
                        "Trilhas na natureza"
                    ],
                    index=0 if 'local' not in st.session_state.respostas else 
                    ["Rua/calçada",
                     "Parques/praças",
                     "Esteira (academia ou casa)",
                     "Pista de atletismo",
                     "Trilhas na natureza"].index(st.session_state.respostas['local'])
                )
        
        # ETAPA 6: Estilo de Vida
        elif st.session_state.etapa_formulario == 6:
            with st.container():
                st.subheader("🌟 ESTILO DE VIDA")
                sono = st.slider(
                    "17. Qualidade do seu sono?",
                    min_value=1, max_value=5, 
                    value=st.session_state.respostas.get('sono', 3),
                    help="1 = Muito ruim, 5 = Excelente"
                )
                
                estresse = st.slider(
                    "18. Como lida com o estresse?",
                    min_value=1, max_value=5, 
                    value=st.session_state.respostas.get('estresse', 3),
                    help="1 = Muito mal, 5 = Muito bem"
                )
                
                lesoes = st.selectbox(
                    "19. Você já teve lesões ou sente dores em:",
                    [
                        "Não tenho dores ou lesões",
                        "Joelhos",
                        "Tornozelos/pés",
                        "Quadril/lombar",
                        "Ombros/pescoço",
                        "Outras regiões"
                    ],
                    index=0 if 'lesoes' not in st.session_state.respostas else 
                    ["Não tenho dores ou lesões",
                     "Joelhos",
                     "Tornozelos/pés",
                     "Quadril/lombar",
                     "Ombros/pescoço",
                     "Outras regiões"].index(st.session_state.respostas['lesoes'])
                )
                
                preferencia_social = st.selectbox(
                    "20. Como prefere treinar?",
                    [
                        "Sozinho(a) - prefiro meu próprio ritmo",
                        "Com um(a) parceiro(a) de treino",
                        "Em pequenos grupos (3-5 pessoas)",
                        "Em grupos maiores/assessorias",
                        "Não tenho preferência"
                    ],
                    index=0 if 'preferencia_social' not in st.session_state.respostas else 
                    ["Sozinho(a) - prefiro meu próprio ritmo",
                     "Com um(a) parceiro(a) de treino",
                     "Em pequenos grupos (3-5 pessoas)",
                     "Em grupos maiores/assessorias",
                     "Não tenho preferência"].index(st.session_state.respostas['preferencia_social'])
                )
        
        # ===============================================
        # CORREÇÃO DOS BOTÕES - AGORA LADO A LADO
        # ===============================================
        voltar_clicado = False
        proximo_clicado = False
        submit_final = False
        
        # Contêiner dedicado para botões
        with st.container():
            # Última etapa - layout diferente
            if st.session_state.etapa_formulario == len(ETAPAS) - 1:
                # Botão Voltar à esquerda (se aplicável)
                if st.session_state.etapa_formulario > 0:
                    col1, _ = st.columns(2)
                    with col1:
                        voltar_clicado = form.form_submit_button(
                            "⬅️ Voltar",
                            use_container_width=True,
                            help="Retornar à etapa anterior"
                        )
                
                # Botão principal abaixo
                submit_final = form.form_submit_button(
                    "🚀 GERAR MEU PLANO!", 
                    type="primary",
                    use_container_width=True,
                    help="Finalizar e gerar seu plano personalizado"
                )
            
            # Etapas intermediárias - botões lado a lado
            else:
                # Criar colunas para posicionamento
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.session_state.etapa_formulario > 0:
                        voltar_clicado = form.form_submit_button(
                            "⬅️ Voltar", 
                            use_container_width=True,
                            help="Retornar à etapa anterior"
                        )
                
                with col2:
                    proximo_clicado = form.form_submit_button(
                        "Próximo ➡️",
                        use_container_width=True,
                        help="Avançar para a próxima etapa"
                    )

        # ===============================================
        # LÓGICA DE PROCESSAMENTO (PERMANECE IGUAL)
        # ===============================================
        if voltar_clicado:
            st.session_state.etapa_formulario -= 1
            st.rerun()
            
        if proximo_clicado:
            # Validação específica para a etapa 0
            if st.session_state.etapa_formulario == 0:
                erros = []
                
                # Validar nome
                if not nome:
                    erros.append("Por favor, informe seu nome")
                
                # Validar telefone
                telefone_formatado = formatar_tel(telefone_input)
                if telefone_formatado is None:
                    erros.append("Por favor, informe um telefone válido com 11 dígitos: (99) 99999-9999)")
                
                # Se houver erros, mostrar mas não avançar
                if erros:
                    st.session_state.erros_etapa1 = erros
                    st.rerun()
                else:
                    # Salvar dados e avançar
                    st.session_state.respostas.update({
                        'nome': nome,
                        'telefone': telefone_formatado,
                        'telefone_input': telefone_input,
                        'idade': idade,
                        'sexo': sexo
                    })
                    st.session_state.etapa_formulario += 1
                    st.rerun()
            
            # Para outras etapas, apenas salvar e avançar
            else:
                # Salva as respostas na etapa atual
                if st.session_state.etapa_formulario == 1:
                    st.session_state.respostas.update({
                        'inatividade': inatividade,
                        'experiencia': experiencia
                    })
                elif st.session_state.etapa_formulario == 2:
                    st.session_state.respostas.update({
                        'saude': saude,
                        'medicamentos': medicamentos,
                        'liberacao_medica': liberacao_medica
                    })
                elif st.session_state.etapa_formulario == 3:
                    st.session_state.respostas.update({
                        'condicao_fisica': condicao_fisica,
                        'escada': escada,
                        'caminhada': caminhada
                    })
                elif st.session_state.etapa_formulario == 4:
                    st.session_state.respostas.update({
                        'objetivo': objetivo,
                        'motivacao': motivacao
                    })
                elif st.session_state.etapa_formulario == 5:
                    st.session_state.respostas.update({
                        'dias_semana': dias_semana,
                        'tempo_treino': tempo_treino,
                        'horario': horario,
                        'local': local
                    })
                
                # Avançar para próxima etapa
                st.session_state.etapa_formulario += 1
                st.rerun()
        
        # Validação e processamento final
        if submit_final:
            # Salvar dados da última etapa
            st.session_state.respostas.update({
                'sono': sono,
                'estresse': estresse,
                'lesoes': lesoes,
                'preferencia_social': preferencia_social
            })
            
            # Validar campos obrigatórios
            erros = []
            if not st.session_state.respostas.get('nome', ''):
                erros.append("Por favor, informe seu nome")
                
            telefone_valido = st.session_state.respostas.get('telefone', '')
            if not telefone_valido:
                erros.append("Por favor, informe seu telefone")
            
            if erros:
                st.session_state.etapa_formulario = 0
                st.session_state.erros_etapa1 = erros
                st.rerun()
            else:
                st.session_state.form_valido = True

    # Processamento externo (fora do formulário) se o formulário for válido
    if st.session_state.form_valido:
        respostas = st.session_state.respostas
        
        # Calcular classificação e gerar programa
        classificacao = calcular_classificacao(respostas)
        restricoes = identificar_restricoes(respostas)
        programa = gerar_programa_treino(classificacao, respostas)
        adaptacao = adaptar_por_objetivo(programa, respostas['objetivo'])
        exercicios = gerar_exercicios_complementares()
        
        with st.spinner('💾 Analisando suas respostas e criando seu plano...'):
            sucesso, mensagem_erro = salvar_dados_sheets(respostas, classificacao)
            if sucesso:
                st.toast("Dados Calculados com sucesso!", icon="✅")
        
        # Efeito visual de confetes
        st.balloons()
        st.success("**Seu plano personalizado está pronto!, Baixe em PDF ao final do resumo**")
        
        # Cartão de resumo
        with st.container():
            #st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f"### 📋 Resumo do Seu Plano")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Perfil", classificacao)
                st.metric("Duração", programa['duracao'])
            with col2:
                st.metric("Dias/Semana", respostas['dias_semana'])
                st.metric("Objetivo", respostas['objetivo'].split('/')[0])
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gerar PDF
        pdf_buffer, pdf_erro = gerar_pdf(
            respostas, classificacao, programa, 
            adaptacao, exercicios, restricoes
        )
        
        if pdf_buffer:
            # Mensagem informativa sobre o conteúdo completo no PDF
            st.info("""
            📄 **O plano de treino completo está disponível apenas no PDF**, incluindo:
            - Detalhamento completo das fases de treinamento
            - Exercícios complementares específicos
            - Adaptações para seu objetivo
            - Dicas personalizadas
            """)

            # Botão de download
            st.download_button(
                label="📥 BAIXAR PROGRAMA EM PDF",
                data=pdf_buffer.getvalue(),
                file_name=f"programa_corrida_{classificacao.lower()}_{datetime.datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_button",
                type= "primary",
                help="Clique para baixar seu programa completo"
            )
        else:
            st.error(f"Erro ao gerar PDF: {pdf_erro}")
       
        if restricoes:
            st.warning("⚠️ **ATENÇÕES ESPECIAIS IDENTIFICADAS:**")
            for restricao in restricoes:
                st.write(f"• {restricao}")
        
        # Resetar estado para evitar reexecução
        st.session_state.form_valido = False
        st.session_state.etapa_formulario = 0
        st.session_state.respostas = {}
        st.session_state.erros_etapa1 = []
        "---"

if __name__ == "__main__":
    main()