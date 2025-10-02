def calcular_classificacao(respostas):
    """Calcula a classificação do usuário baseada nas respostas"""
    score_condicao = 0
    score_experiencia = 0
    
    # Pontuação baseada na condição física atual
    if respostas['condicao_fisica'] >= 4:
        score_condicao = 3
    elif respostas['condicao_fisica'] == 3:
        score_condicao = 2
    else:
        score_condicao = 1
    
    # Pontuação baseada na experiência
    if respostas['inatividade'] == "Pratico atualmente (pelo menos 2x por semana)":
        score_experiencia = 3
    elif respostas['inatividade'] == "Parei há menos de 6 meses":
        score_experiencia = 2
    else:
        score_experiencia = 1
    
    # Ajustes baseados em outros fatores
    if respostas['caminhada'] == "Mais de 45 minutos":
        score_condicao += 1
    elif respostas['caminhada'] == "Menos de 10 minutos":
        score_condicao -= 1
    
    score_total = score_condicao + score_experiencia
    
    if score_total <= 3:
        return "SEDENTÁRIO"
    elif score_total <= 5:
        return "INICIANTE"
    else:
        return "INICIANTE ATIVO"

def identificar_restricoes(respostas):
    """Identifica restrições e necessidades especiais"""
    restricoes = []
    
    if respostas['saude'] != "Não tenho nenhuma condição":
        restricoes.append("ATENÇÃO MÉDICA OBRIGATÓRIA")
    
    if respostas['medicamentos'] == "Sim, e pode afetar exercícios":
        restricoes.append("MONITORAMENTO ESPECIAL NECESSÁRIO")
    
    if respostas['liberacao_medica'] == "Pretendo consultar um médico antes":
        restricoes.append("AGUARDAR LIBERAÇÃO MÉDICA")
    
    if respostas['lesoes'] != "Não tenho dores ou lesões":
        restricoes.append("ATENÇÃO ESPECIAL ÀS ARTICULAÇÕES")
    
    return restricoes

def gerar_programa_treino(classificacao, respostas):
    """Gera o programa de treino baseado na classificação"""
    
    programas = {
        "SEDENTÁRIO": {
            "duracao": "12-16 semanas",
            "fases": [
                {
                    "nome": "FASE 1 - ADAPTAÇÃO",
                    "semanas": "1-4",
                    "frequencia": "3x/semana, dias alternados",
                    "duracao": "20-25 minutos",
                    "estrutura": [
                        "5 min: Aquecimento (caminhada lenta)",
                        "15 min: Caminhada moderada",
                        "5 min: Relaxamento (caminhada lenta)"
                    ]
                },
                {
                    "nome": "FASE 2 - INTRODUÇÃO À CORRIDA",
                    "semanas": "5-8",
                    "frequencia": "3x/semana",
                    "duracao": "25-30 minutos",
                    "estrutura": [
                        "5 min: Aquecimento",
                        "20 min: 1 min corrida + 2 min caminhada (6-7x)",
                        "5 min: Relaxamento"
                    ]
                },
                {
                    "nome": "FASE 3 - CONSOLIDAÇÃO",
                    "semanas": "9-12",
                    "frequencia": "3-4x/semana",
                    "duracao": "30-35 minutos",
                    "estrutura": [
                        "5 min: Aquecimento",
                        "25 min: 2 min corrida + 1 min caminhada (8-9x)",
                        "5 min: Relaxamento"
                    ]
                }
            ]
        },
        "INICIANTE": {
            "duracao": "8-12 semanas",
            "fases": [
                {
                    "nome": "FASE 1 - BASE",
                    "semanas": "1-4",
                    "frequencia": "3x/semana",
                    "duracao": "25-30 minutos",
                    "estrutura": [
                        "5 min: Aquecimento",
                        "20 min: Alternância 2 min corrida + 1 min caminhada",
                        "5 min: Relaxamento"
                    ]
                },
                {
                    "nome": "FASE 2 - PROGRESSÃO",
                    "semanas": "5-8",
                    "frequencia": "3-4x/semana",
                    "duracao": "30-35 minutos",
                    "estrutura": [
                        "5 min: Aquecimento",
                        "25 min: 15 min corrida + 5 min caminhada + 5 min corrida",
                        "5 min: Relaxamento"
                    ]
                }
            ]
        },
        "INICIANTE ATIVO": {
            "duracao": "6-8 semanas",
            "fases": [
                {
                    "nome": "FASE 1 - RETOMADA",
                    "semanas": "1-3",
                    "frequencia": "3-4x/semana",
                    "duracao": "30-35 minutos",
                    "estrutura": [
                        "5 min: Aquecimento",
                        "20-25 min: Corrida leve contínua",
                        "5 min: Relaxamento"
                    ]
                },
                {
                    "nome": "FASE 2 - CONSOLIDAÇÃO",
                    "semanas": "4-6",
                    "frequencia": "4x/semana",
                    "duracao": "35-45 minutos",
                    "estrutura": [
                        "5 min: Aquecimento",
                        "30-35 min: Corrida contínua + 1x intervalos/semana",
                        "5 min: Relaxamento"
                    ]
                }
            ]
        }
    }
    
    return programas[classificacao]

def adaptar_por_objetivo(programa, objetivo):
    """Adapta o programa baseado no objetivo principal"""
    adaptacoes = {
        "Emagrecimento/perda de peso": {
            "modificacao": "Aumentar duração em 20%, manter intensidade moderada",
            "sessoes_extras": "Adicionar 1-2 sessões de caminhada nos dias de descanso",
            "dica": "Foque no volume (duração) ao invés da velocidade"
        },
        "Melhorar a saúde geral": {
            "modificacao": "Manter programa padrão com foco na consistência",
            "sessoes_extras": "Exercícios de fortalecimento 2x/semana",
            "dica": "Regularidade é mais importante que intensidade"
        },
        "Reduzir estresse/bem-estar mental": {
            "modificacao": "Priorizar ambientes agradáveis, intensidade confortável",
            "sessoes_extras": "Sessões de caminhada meditativa",
            "dica": "Escolha locais que te tragam paz (parques, natureza)"
        },
        "Participar de provas/competições": {
            "modificacao": "Após 8 semanas, incluir 1 treino intervalado/semana",
            "sessoes_extras": "Treino longo aos finais de semana",
            "dica": "Defina uma prova de 5K como primeira meta"
        }
    }
    return adaptacoes.get(objetivo, adaptacoes["Melhorar a saúde geral"])

def gerar_exercicios_complementares():
    """Retorna exercícios complementares essenciais"""
    return {
        "Fortalecimento (2-3x/semana)": [
            "Prancha: 3x 20-60s (progressivo)",
            "Agachamento: 3x 10-15",
            "Afundo: 3x 10 cada perna",
            "Glúteo bridge: 3x 15-20",
            "Panturrilha: 3x 15-20"
        ],
        "Mobilidade Pré-treino (5-8 min)": [
            "Elevação de joelhos: 30s",
            "Chute ao glúteo: 30s",
            "Passada lateral: 30s cada lado",
            "Círculos de braço: 30s",
            "Balanço de pernas: 30s cada lado"
        ],
        "Alongamento Pós-treino (10-15 min)": [
            "Panturrilha: 30s cada perna",
            "Posterior de coxa: 30s cada perna",
            "Quadríceps: 30s cada perna",
            "Flexor do quadril: 30s cada lado",
            "Lombar e peito: 30s cada"
        ]
    }