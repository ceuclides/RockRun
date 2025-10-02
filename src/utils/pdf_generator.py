import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def gerar_pdf(dados_usuario, classificacao, programa, adaptacao, exercicios, restricoes):
    """Gera PDF com o programa personalizado"""
    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#FF6B35'),
            alignment=1  # Centro
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2E86AB')
        )
        
        story = []

        # Título
        story.append(Paragraph("PROGRAMA PERSONALIZADO DE CORRIDA", title_style))
        story.append(Spacer(1, 1))
        
        #nome do usuário
        story.append(Paragraph(f"Olá, <b>{dados_usuario['nome']}</b>! Este Plano foi gerado com base em suas respostas ao questionário, levando em consideração as melhores práticas de recomendação de corrida. Refaça-o sempre que perceber sua evolução, ou qualquer alteração em seu estado físico.", styles['Normal']))
   
        # Data
        story.append(Paragraph(f"Gerado em:<b>{datetime.now().strftime('%d/%m/%Y')}</b>", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Classificação
        story.append(Paragraph("CLASSIFICAÇÃO", heading_style))
        story.append(Paragraph(f"Perfil: <b>{classificacao}</b>", styles['Normal']))
        story.append(Paragraph(f"Duração do programa: <b>{programa['duracao']}</b>", styles['Normal']))
        story.append(Spacer(1, 1))
        
        # Restrições (se houver)
        if restricoes:
            story.append(Paragraph("ATENÇÕES ESPECIAIS", heading_style))
            for restricao in restricoes:
                story.append(Paragraph(f"• {restricao}", styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Programa de treino
        story.append(Paragraph("PROGRAMA DE TREINO", heading_style))
        for fase in programa['fases']:
            story.append(Paragraph(f"<b>{fase['nome']} (Semanas {fase['semanas']})</b>", styles['Normal']))
            story.append(Paragraph(f"Frequência: {fase['frequencia']}", styles['Normal']))
            story.append(Paragraph(f"Duração: {fase['duracao']}", styles['Normal']))
            story.append(Paragraph("Estrutura:", styles['Normal']))
            for item in fase['estrutura']:
                story.append(Paragraph(f"• {item}", styles['Normal']))
            story.append(Spacer(1, 8))
        
        # Adaptação por objetivo
        story.append(Paragraph("ADAPTAÇÃO PARA SEU OBJETIVO", heading_style))
        story.append(Paragraph(f"<b>Modificação:</b> {adaptacao['modificacao']}", styles['Normal']))
        story.append(Paragraph(f"<b>Sessões extras:</b> {adaptacao['sessoes_extras']}", styles['Normal']))
        story.append(Paragraph(f"<b>Dica especial:</b> {adaptacao['dica']}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Exercícios complementares
        story.append(Paragraph("EXERCÍCIOS COMPLEMENTARES", heading_style))
        for categoria, exercicios_cat in exercicios.items():
            story.append(Paragraph(f"<b>{categoria}:</b>", styles['Normal']))
            for exercicio in exercicios_cat:
                story.append(Paragraph(f"• {exercicio}", styles['Normal']))
            story.append(Spacer(1, 8))
        
        # Dicas importantes
        #story.append(PageBreak())
        story.append(Paragraph("DICAS IMPORTANTES PARA O SUCESSO", heading_style))
        
        dicas = [
            "Comece devagar e seja consistente - é melhor correr pouco regularmente do que muito esporadicamente",
            "Escute seu corpo - dor não é normal, desconforto muscular leve é esperado",
            "Hidrate-se bem antes, durante e após os treinos",
            "Use tênis adequado para corrida e substitua a cada 500-800km",
            "Aqueça antes e alongue depois de cada sessão",
            "Registre seus treinos para acompanhar a evolução",
            "Tenha paciência - os resultados vêm com o tempo",
            "Em caso de dúvidas, consulte um profissional de educação física"
        ]
        
        for dica in dicas:
            story.append(Paragraph(f"• {dica}", styles['Normal']))
            story.append(Spacer(1, 4))
        
        # Sinais de alerta
        story.append(Spacer(1, 12))
        story.append(Paragraph("SINAIS DE ALERTA - PROCURE ORIENTAÇÃO", heading_style))
        
        alertas = [
            "Dores articulares persistentes",
            "Fadiga excessiva que não melhora com descanso",
            "Tontura ou desmaios",
            "Lesões que não cicatrizam",
            "Perda de motivação extrema ou sintomas depressivos"
        ]
        
        for alerta in alertas:
            story.append(Paragraph(f"• {alerta}", styles['Normal']))
            story.append(Spacer(1, 4))
        
        # Rodapé
        story.append(Spacer(1, 20))
        story.append(Paragraph("Boa corrida e lembre-se: cada passo conta!", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer, ""  # Sucesso
    except Exception as e:
        return None, f"Erro ao gerar PDF: {str(e)}"