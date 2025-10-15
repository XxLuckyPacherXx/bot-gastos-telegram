#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot do Telegram para Controle de Gastos de Construção
Versão Railway - Service Account
"""

import os
import sys
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import gspread
from google.oauth2.service_account import Credentials

# ========== CONFIGURAÇÕES ==========
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GOOGLE_CREDENTIALS_JSON = os.environ.get('GOOGLE_CREDENTIALS_JSON', '')

# Verificar configurações
if not TELEGRAM_BOT_TOKEN:
    print("❌ ERRO: TELEGRAM_BOT_TOKEN não configurado!")
    sys.exit(1)

if not OPENAI_API_KEY:
    print("❌ ERRO: OPENAI_API_KEY não configurado!")
    sys.exit(1)

if not GOOGLE_CREDENTIALS_JSON:
    print("❌ ERRO: GOOGLE_CREDENTIALS_JSON não configurado!")
    sys.exit(1)

# Cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Scopes do Google
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# ========== FUNÇÕES DO GOOGLE SHEETS ==========

def obter_cliente_google():
    """Obtém cliente autenticado do Google Sheets usando Service Account"""
    try:
        # Carregar credenciais da variável de ambiente
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"❌ Erro ao autenticar Google: {e}")
        return None

def criar_planilha_obra(gc, nome_obra):
    """Cria uma nova planilha no Google Sheets"""
    nome_planilha = f"Obra: {nome_obra}"
    
    # Criar planilha
    spreadsheet = gc.create(nome_planilha)
    
    # Configurar abas
    sheet = spreadsheet.sheet1
    sheet.update_title("Gastos")
    
    # Cabeçalho Gastos
    sheet.update('A1', f"GASTOS - OBRA: {nome_obra.upper()}")
    sheet.format('A1', {
        "textFormat": {"bold": True, "fontSize": 14},
        "horizontalAlignment": "CENTER"
    })
    
    sheet.update('A2:E2', [['Data', 'Descrição', 'Categoria', 'Valor', 'Observações']])
    sheet.format('A2:E2', {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8}
    })
    
    # Ajustar larguras
    sheet.set_column_width(1, 100)   # A - Data
    sheet.set_column_width(2, 300)   # B - Descrição
    sheet.set_column_width(3, 150)   # C - Categoria
    sheet.set_column_width(4, 120)   # D - Valor
    sheet.set_column_width(5, 300)   # E - Observações
    
    # Aba Pagamentos
    ws_pag = spreadsheet.add_worksheet("Pagamentos", 1000, 5)
    ws_pag.update('A1', f"PAGAMENTOS - OBRA: {nome_obra.upper()}")
    ws_pag.format('A1', {
        "textFormat": {"bold": True, "fontSize": 14},
        "horizontalAlignment": "CENTER"
    })
    
    ws_pag.update('A2:E2', [['Data', 'Funcionário', 'Função', 'Valor', 'Observações']])
    ws_pag.format('A2:E2', {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 0.8, "green": 0.8, "blue": 0.8}
    })
    
    # Ajustar larguras
    ws_pag.set_column_width(1, 100)
    ws_pag.set_column_width(2, 200)
    ws_pag.set_column_width(3, 150)
    ws_pag.set_column_width(4, 120)
    ws_pag.set_column_width(5, 300)
    
    # Aba Resumo
    ws_resumo = spreadsheet.add_worksheet("Resumo", 100, 5)
    ws_resumo.update('A1', f"RESUMO - OBRA: {nome_obra.upper()}")
    ws_resumo.format('A1', {
        "textFormat": {"bold": True, "fontSize": 14},
        "horizontalAlignment": "CENTER"
    })
    
    ws_resumo.update('A3:B6', [
        ['Total de Gastos:', '=SOMA(Gastos!D:D)'],
        ['Total de Pagamentos:', '=SOMA(Pagamentos!D:D)'],
        ['', ''],
        ['TOTAL GERAL:', '=B3+B4']
    ])
    
    ws_resumo.format('A3:A6', {"textFormat": {"bold": True}})
    ws_resumo.format('B6', {
        "textFormat": {"bold": True, "fontSize": 12},
        "backgroundColor": {"red": 1, "green": 0.9, "blue": 0.6}
    })
    
    return spreadsheet

def adicionar_gasto(gc, nome_obra, data, descricao, categoria, valor, obs=""):
    """Adiciona um gasto à planilha"""
    nome_planilha = f"Obra: {nome_obra}"
    
    try:
        spreadsheet = gc.open(nome_planilha)
    except:
        spreadsheet = criar_planilha_obra(gc, nome_obra)
    
    sheet = spreadsheet.worksheet("Gastos")
    sheet.append_row([data, descricao, categoria, valor, obs])
    
    return spreadsheet.url

def adicionar_pagamento(gc, nome_obra, data, funcionario, funcao, valor, obs=""):
    """Adiciona um pagamento à planilha"""
    nome_planilha = f"Obra: {nome_obra}"
    
    try:
        spreadsheet = gc.open(nome_planilha)
    except:
        spreadsheet = criar_planilha_obra(gc, nome_obra)
    
    sheet = spreadsheet.worksheet("Pagamentos")
    sheet.append_row([data, funcionario, funcao, valor, obs])
    
    return spreadsheet.url

# ========== FUNÇÕES DE IA ==========

def transcrever_audio(audio_path):
    """Transcreve áudio usando Whisper da OpenAI"""
    with open(audio_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="pt"
        )
    return transcript.text

def extrair_informacoes(texto):
    """Extrai informações do texto usando GPT"""
    prompt = f"""
Analise o seguinte texto sobre gastos ou pagamentos de uma obra de construção e extraia as informações:

Texto: "{texto}"

Identifique:
1. TIPO: É um "gasto" (compra de material/serviço) ou "pagamento" (pagamento a funcionário)?
2. OBRA: Nome da obra mencionada (se não mencionar, use "Obra Padrão")
3. Se for GASTO:
   - DESCRIÇÃO: O que foi comprado
   - CATEGORIA: Materiais, Ferramentas, Transporte, Aluguel, ou Outros
   - VALOR: Valor em reais
   - OBSERVAÇÕES: Informações adicionais
4. Se for PAGAMENTO:
   - FUNCIONÁRIO: Nome do funcionário
   - FUNÇÃO: Pedreiro, Ajudante, Eletricista, Encanador, Servente, ou Outros
   - VALOR: Valor em reais
   - OBSERVAÇÕES: Informações adicionais

Responda APENAS no formato JSON:
{{
  "tipo": "gasto" ou "pagamento",
  "obra": "nome da obra",
  "descricao": "descrição" (se gasto),
  "categoria": "categoria" (se gasto),
  "funcionario": "nome" (se pagamento),
  "funcao": "função" (se pagamento),
  "valor": "valor numérico",
  "observacoes": "observações"
}}
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    
    resultado = json.loads(response.choices[0].message.content)
    return resultado

# ========== HANDLERS DO BOT ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    mensagem = """
🤖 *Bot de Controle de Gastos de Construção*

Envie um áudio descrevendo:
• Gastos (materiais, ferramentas, etc.)
• Pagamentos (funcionários)

Exemplo de áudio:
_"Comprei cimento por 200 reais para a obra do João"_
_"Paguei o pedreiro Pedro 350 reais da obra da Maria"_

O bot vai criar/atualizar automaticamente uma planilha no Google Drive!
"""
    await update.message.reply_text(mensagem, parse_mode='Markdown')

async def processar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processa áudio enviado"""
    try:
        await update.message.reply_text("🎤 Recebendo áudio...")
        
        # Baixar áudio
        audio_file = await update.message.voice.get_file()
        audio_path = f"audio_{update.message.voice.file_unique_id}.ogg"
        await audio_file.download_to_drive(audio_path)
        
        await update.message.reply_text("📝 Transcrevendo...")
        
        # Transcrever
        texto = transcrever_audio(audio_path)
        os.remove(audio_path)
        
        await update.message.reply_text(f"✅ Transcrição: _{texto}_", parse_mode='Markdown')
        await update.message.reply_text("🤖 Processando informações...")
        
        # Extrair informações
        info = extrair_informacoes(texto)
        
        # Obter cliente Google
        gc = obter_cliente_google()
        if not gc:
            await update.message.reply_text("❌ Erro ao conectar com Google Drive!")
            return
        
        # Adicionar à planilha
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        
        if info['tipo'] == 'gasto':
            url = adicionar_gasto(
                gc,
                info['obra'],
                data_hoje,
                info.get('descricao', ''),
                info.get('categoria', 'Outros'),
                f"R$ {info['valor']}",
                info.get('observacoes', '')
            )
            
            mensagem = f"""
✅ *Gasto Registrado!*

📊 *Obra:* {info['obra']}
📦 *Item:* {info.get('descricao', '')}
🏷️ *Categoria:* {info.get('categoria', '')}
💰 *Valor:* R$ {info['valor']}
📅 *Data:* {data_hoje}

🔗 [Abrir Planilha]({url})
"""
        else:  # pagamento
            url = adicionar_pagamento(
                gc,
                info['obra'],
                data_hoje,
                info.get('funcionario', ''),
                info.get('funcao', 'Outros'),
                f"R$ {info['valor']}",
                info.get('observacoes', '')
            )
            
            mensagem = f"""
✅ *Pagamento Registrado!*

📊 *Obra:* {info['obra']}
👷 *Funcionário:* {info.get('funcionario', '')}
🔧 *Função:* {info.get('funcao', '')}
💰 *Valor:* R$ {info['valor']}
📅 *Data:* {data_hoje}

🔗 [Abrir Planilha]({url})
"""
        
        await update.message.reply_text(mensagem, parse_mode='Markdown')
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        await update.message.reply_text(f"❌ Erro ao processar: {str(e)}")

# ========== MAIN ==========

def main():
    """Função principal"""
    print("=" * 70)
    print("🤖 BOT DO TELEGRAM RAILWAY INICIADO!")
    print("=" * 70)
    print("✅ Bot funcionando!")
    print("📊 Armazenamento: Google Drive (Service Account)")
    print("🔐 Autenticação: Service Account")
    print("=" * 70)
    
    # Criar aplicação
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VOICE, processar_audio))
    
    # Iniciar
    print("🚀 Bot pronto para receber mensagens!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

