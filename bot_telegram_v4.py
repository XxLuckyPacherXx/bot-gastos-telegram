#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot do Telegram para Controle de Gastos - Versão 4.0 CLOUD
Com Google Planilhas e hospedagem em nuvem
Autor: Manus AI
Data: 14/10/2025
"""

import os
import json
import re
import tempfile
import requests
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# ============================================================
# CONFIGURAÇÃO - Variáveis de Ambiente
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
GOOGLE_CREDENTIALS_JSON = os.environ.get('GOOGLE_CREDENTIALS_JSON')
# ============================================================

# Configurar Google Sheets
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def get_google_client():
    """Conecta ao Google Sheets"""
    if not GOOGLE_CREDENTIALS_JSON:
        raise Exception("GOOGLE_CREDENTIALS_JSON não configurado!")
    
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def normalizar_nome_obra(nome):
    """Normaliza o nome da obra para nome de planilha"""
    nome = nome.lower()
    nome = re.sub(r'[àáâãäå]', 'a', nome)
    nome = re.sub(r'[èéêë]', 'e', nome)
    nome = re.sub(r'[ìíîï]', 'i', nome)
    nome = re.sub(r'[òóôõö]', 'o', nome)
    nome = re.sub(r'[ùúûü]', 'u', nome)
    nome = re.sub(r'[ç]', 'c', nome)
    nome = re.sub(r'[^a-z0-9\s]', '', nome)
    nome = re.sub(r'\s+', ' ', nome.strip())
    return nome.title()

def transcrever_audio(audio_path):
    """Transcreve áudio usando Whisper via API HTTP"""
    url = "https://api.openai.com/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    with open(audio_path, 'rb') as audio_file:
        files = {
            'file': audio_file,
            'model': (None, 'whisper-1'),
            'language': (None, 'pt')
        }
        
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            return response.json()['text']
        else:
            raise Exception(f"Erro na transcrição: {response.text}")

def extrair_informacoes(texto_transcrito):
    """Extrai informações do texto transcrito usando LLM via API HTTP"""
    url = "https://api.openai.com/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Analise o seguinte texto sobre um gasto de construção e extraia as informações em formato JSON.

Texto: "{texto_transcrito}"

IMPORTANTE: 
1. Identifique o NOME DA OBRA (ex: "obra do João", "obra da rua 10", "obra do centro")
2. Identifique se é PAGAMENTO DE FUNCIONÁRIO ou GASTO GERAL

PALAVRAS-CHAVE para PAGAMENTO:
- "paguei", "pagamento", "salário", "mão de obra", "funcionário"
- Menção a pessoa + função: "pedreiro João", "ajudante Pedro"
- Funções: "pedreiro", "ajudante", "servente", "mestre de obras", "eletricista", "encanador"

Se for pagamento de funcionário:
{{
  "tipo": "pagamento",
  "obra": "nome da obra identificado",
  "data": "DD/MM/YYYY",
  "nome_funcionario": "nome do funcionário",
  "funcao": "função (pedreiro, ajudante, etc.)",
  "valor": valor numérico,
  "observacoes": "informações adicionais"
}}

Se for gasto geral:
{{
  "tipo": "gasto",
  "obra": "nome da obra identificado",
  "data": "DD/MM/YYYY",
  "descricao": "descrição do item",
  "categoria": "Ferramentas, Materiais, Transporte ou Outros",
  "valor": valor numérico,
  "observacoes": "informações adicionais"
}}

Se não conseguir identificar a obra, use "obra": "geral"

Data de hoje: {datetime.now().strftime('%d/%m/%Y')}

Responda APENAS com um objeto JSON válido, sem texto adicional.
"""
    
    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": "Você é um assistente que extrai informações de gastos de construção. Sempre responda apenas com JSON válido."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        resposta = response.json()['choices'][0]['message']['content'].strip()
        
        if resposta.startswith('```'):
            resposta = re.sub(r'^```json?\s*', '', resposta)
            resposta = re.sub(r'\s*```$', '', resposta)
        
        return json.loads(resposta)
    else:
        raise Exception(f"Erro na extração: {response.text}")

def criar_planilha_obra(gc, nome_obra):
    """Cria uma nova planilha no Google Sheets"""
    nome_planilha = f"Obra: {nome_obra}"
    
    # Criar planilha
    spreadsheet = gc.create(nome_planilha)
    
    # Compartilhar com o usuário (tornar editável)
    # Nota: Você pode adicionar seu email aqui para ter acesso direto
    # spreadsheet.share('seu_email@gmail.com', perm_type='user', role='writer')
    
    # Configurar abas
    sheet = spreadsheet.sheet1
    sheet.update_title("Gastos")
    
    # Aba Gastos - Cabeçalho
    sheet.update('A1', f"GASTOS - OBRA: {nome_obra.upper()}")
    sheet.format('A1', {
        "textFormat": {"bold": True, "fontSize": 14},
        "backgroundColor": {"red": 0.2, "green": 0.38, "blue": 0.57}
    })
    sheet.merge_cells('A1:E1')
    
    headers_gastos = [["Data", "Descrição do Item", "Categoria", "Valor (R$)", "Observações"]]
    sheet.update('A2:E2', headers_gastos)
    sheet.format('A2:E2', {
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "backgroundColor": {"red": 0.2, "green": 0.38, "blue": 0.57},
        "horizontalAlignment": "CENTER"
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
        "backgroundColor": {"red": 0.2, "green": 0.38, "blue": 0.57}
    })
    ws_pag.merge_cells('A1:E1')
    
    headers_pag = [["Data", "Nome do Funcionário", "Função", "Valor (R$)", "Observações"]]
    ws_pag.update('A2:E2', headers_pag)
    ws_pag.format('A2:E2', {
        "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
        "backgroundColor": {"red": 0.2, "green": 0.38, "blue": 0.57},
        "horizontalAlignment": "CENTER"
    })
    
    ws_pag.set_column_width(1, 100)   # A - Data
    ws_pag.set_column_width(2, 200)   # B - Nome
    ws_pag.set_column_width(3, 150)   # C - Função
    ws_pag.set_column_width(4, 120)   # D - Valor
    ws_pag.set_column_width(5, 300)   # E - Observações
    
    # Aba Resumo
    ws_resumo = spreadsheet.add_worksheet("Resumo", 100, 2)
    ws_resumo.update('A1', f"RESUMO - OBRA: {nome_obra.upper()}")
    ws_resumo.format('A1', {
        "textFormat": {"bold": True, "fontSize": 14},
        "backgroundColor": {"red": 0.2, "green": 0.38, "blue": 0.57}
    })
    ws_resumo.merge_cells('A1:B1')
    
    ws_resumo.update('A3', "Total Gastos:")
    ws_resumo.update('B3', "=SOMA(Gastos!D:D)")
    ws_resumo.format('B3', {
        "textFormat": {"bold": True},
        "numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}
    })
    
    ws_resumo.update('A4', "Total Pagamentos:")
    ws_resumo.update('B4', "=SOMA(Pagamentos!D:D)")
    ws_resumo.format('B4', {
        "textFormat": {"bold": True},
        "numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}
    })
    
    ws_resumo.update('A6', "TOTAL GERAL:")
    ws_resumo.update('B6', "=B3+B4")
    ws_resumo.format('A6:B6', {
        "textFormat": {"bold": True},
        "backgroundColor": {"red": 1, "green": 0.75, "blue": 0}
    })
    ws_resumo.format('B6', {
        "numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}
    })
    
    ws_resumo.set_column_width(1, 200)
    ws_resumo.set_column_width(2, 150)
    
    return spreadsheet

def obter_planilha_obra(gc, nome_obra):
    """Obtém a planilha da obra, criando se não existir"""
    nome_planilha = f"Obra: {nome_obra}"
    
    try:
        # Tentar abrir planilha existente
        spreadsheet = gc.open(nome_planilha)
        return spreadsheet
    except gspread.SpreadsheetNotFound:
        # Criar nova planilha
        return criar_planilha_obra(gc, nome_obra)

def adicionar_na_planilha(gc, dados):
    """Adiciona os dados na planilha Google Sheets"""
    nome_obra = normalizar_nome_obra(dados.get('obra', 'geral'))
    spreadsheet = obter_planilha_obra(gc, nome_obra)
    
    tipo = dados.get('tipo', 'gasto')
    
    if tipo == 'pagamento':
        sheet = spreadsheet.worksheet("Pagamentos")
        nova_linha = [
            dados.get('data', datetime.now().strftime('%d/%m/%Y')),
            dados.get('nome_funcionario', ''),
            dados.get('funcao', ''),
            float(dados.get('valor', 0)),
            dados.get('observacoes', '')
        ]
    else:
        sheet = spreadsheet.worksheet("Gastos")
        nova_linha = [
            dados.get('data', datetime.now().strftime('%d/%m/%Y')),
            dados.get('descricao', ''),
            dados.get('categoria', 'Outros'),
            float(dados.get('valor', 0)),
            dados.get('observacoes', '')
        ]
    
    # Adicionar linha
    sheet.append_row(nova_linha)
    
    # Formatar valor como moeda
    ultima_linha = len(sheet.get_all_values())
    sheet.format(f'D{ultima_linha}', {
        "numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}
    })
    
    return ultima_linha, sheet.title, nome_obra, spreadsheet.url

def listar_obras(gc):
    """Lista todas as obras cadastradas"""
    obras = []
    spreadsheets = gc.openall()
    
    for sheet in spreadsheets:
        if sheet.title.startswith("Obra: "):
            nome = sheet.title.replace("Obra: ", "")
            obras.append({"nome": nome, "url": sheet.url})
    
    return obras

def processar_audio_telegram(file_path):
    """Processa áudio do Telegram"""
    try:
        if not OPENAI_API_KEY:
            return {
                'sucesso': False,
                'erro': 'Chave da OpenAI não configurada.'
            }
        
        if not GOOGLE_CREDENTIALS_JSON:
            return {
                'sucesso': False,
                'erro': 'Credenciais do Google não configuradas.'
            }
        
        gc = get_google_client()
        texto = transcrever_audio(file_path)
        dados = extrair_informacoes(texto)
        linha, aba, obra, url = adicionar_na_planilha(gc, dados)
        
        return {
            'sucesso': True,
            'transcricao': texto,
            'dados': dados,
            'linha': linha,
            'aba': aba,
            'obra': obra,
            'url': url
        }
    except Exception as e:
        return {
            'sucesso': False,
            'erro': str(e)
        }

def main():
    """Função principal do bot"""
    try:
        import telegram
        from telegram.ext import Application, MessageHandler, CommandHandler, filters
    except ImportError:
        print("❌ Biblioteca python-telegram-bot não encontrada!")
        return
    
    if not TELEGRAM_BOT_TOKEN:
        print("❌ ERRO: TELEGRAM_BOT_TOKEN não configurado!")
        return
    
    async def start(update, context):
        """Comando /start"""
        await update.message.reply_text(
            "🏗️ *Bem-vindo ao Controle de Gastos v4.0 CLOUD!*\n\n"
            "✨ *NOVIDADES:*\n"
            "• Bot rodando na nuvem 24h\n"
            "• Salva no Google Planilhas\n"
            "• Acesse de qualquer lugar\n"
            "• Sem precisar deixar PC ligado\n\n"
            "🎤 *Como usar:*\n"
            "Envie um áudio mencionando:\n"
            "• Nome da obra\n"
            "• O que comprou ou pagou\n"
            "• Valor\n\n"
            "*Exemplos:*\n"
            "\"Comprei cimento por 200 reais para a obra do João\"\n"
            "\"Paguei o pedreiro na obra da rua 10, 350 reais\"\n\n"
            "Use /obras para ver suas planilhas\n"
            "Use /ajuda para mais informações",
            parse_mode='Markdown'
        )
    
    async def ajuda(update, context):
        """Comando /ajuda"""
        await update.message.reply_text(
            "📚 *Como usar o bot v4.0:*\n\n"
            "1️⃣ Grave um áudio de voz\n"
            "2️⃣ Mencione o nome da obra\n"
            "3️⃣ Descreva o gasto ou pagamento\n"
            "4️⃣ Envie para mim\n\n"
            "*Para PAGAMENTOS, use palavras como:*\n"
            "• \"Paguei o pedreiro...\"\n"
            "• \"Pagamento do funcionário...\"\n"
            "• \"Salário do ajudante...\"\n"
            "• \"Mão de obra...\"\n\n"
            "*Para GASTOS, use:*\n"
            "• \"Comprei...\"\n"
            "• \"Gastei com...\"\n"
            "• \"Materiais...\"\n\n"
            "*Comandos:*\n"
            "/start - Iniciar bot\n"
            "/obras - Ver todas as obras\n"
            "/ajuda - Ver esta mensagem\n"
            "/status - Ver status do sistema",
            parse_mode='Markdown'
        )
    
    async def obras(update, context):
        """Comando /obras"""
        try:
            gc = get_google_client()
            lista_obras = listar_obras(gc)
            
            if lista_obras:
                mensagem = f"🏗️ *Obras Cadastradas ({len(lista_obras)}):*\n\n"
                for i, obra in enumerate(lista_obras, 1):
                    mensagem += f"{i}. {obra['nome']}\n"
                    mensagem += f"   🔗 {obra['url']}\n\n"
            else:
                mensagem = "⚠️ Nenhuma obra cadastrada ainda.\n\nEnvie um áudio mencionando uma obra para começar!"
            
            await update.message.reply_text(mensagem, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Erro ao listar obras: {str(e)}")
    
    async def status(update, context):
        """Comando /status"""
        try:
            gc = get_google_client()
            lista_obras = listar_obras(gc)
            total_obras = len(lista_obras)
            
            status_msg = (
                f"✅ Sistema funcionando - v4.0 CLOUD\n\n"
                f"🏗️ *Obras cadastradas:* {total_obras}\n"
                f"☁️ *Hospedagem:* Nuvem (24h)\n"
                f"📊 *Armazenamento:* Google Planilhas\n"
            )
            
            await update.message.reply_text(status_msg, parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ Erro: {str(e)}")
    
    async def processar_audio(update, context):
        """Processa áudio recebido"""
        await update.message.reply_text("⏳ Processando seu áudio...")
        
        try:
            audio = await update.message.voice.get_file()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                await audio.download_to_drive(temp_file.name)
                temp_path = temp_file.name
            
            resultado = processar_audio_telegram(temp_path)
            os.unlink(temp_path)
            
            if resultado['sucesso']:
                dados = resultado['dados']
                tipo = dados.get('tipo', 'gasto')
                obra = resultado['obra']
                
                if tipo == 'pagamento':
                    mensagem = (
                        "✅ *Pagamento registrado com sucesso!*\n\n"
                        f"🏗️ *Obra:* {obra}\n"
                        f"📝 *Transcrição:*\n{resultado['transcricao']}\n\n"
                        f"📅 *Data:* {dados['data']}\n"
                        f"👤 *Funcionário:* {dados['nome_funcionario']}\n"
                        f"🔧 *Função:* {dados['funcao']}\n"
                        f"💰 *Valor:* R$ {dados['valor']:.2f}\n"
                        f"📌 *Observações:* {dados.get('observacoes', '-')}\n\n"
                        f"📊 *Aba:* {resultado['aba']}\n"
                        f"✔️ Adicionado na linha {resultado['linha']}!\n\n"
                        f"🔗 Abrir planilha: {resultado['url']}"
                    )
                else:
                    mensagem = (
                        "✅ *Gasto registrado com sucesso!*\n\n"
                        f"🏗️ *Obra:* {obra}\n"
                        f"📝 *Transcrição:*\n{resultado['transcricao']}\n\n"
                        f"📅 *Data:* {dados['data']}\n"
                        f"🏷️ *Descrição:* {dados['descricao']}\n"
                        f"📦 *Categoria:* {dados['categoria']}\n"
                        f"💰 *Valor:* R$ {dados['valor']:.2f}\n"
                        f"📌 *Observações:* {dados.get('observacoes', '-')}\n\n"
                        f"📊 *Aba:* {resultado['aba']}\n"
                        f"✔️ Adicionado na linha {resultado['linha']}!\n\n"
                        f"🔗 Abrir planilha: {resultado['url']}"
                    )
                
                await update.message.reply_text(mensagem, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    f"❌ Erro ao processar: {resultado['erro']}"
                )
        
        except Exception as e:
            await update.message.reply_text(
                f"❌ Erro inesperado: {str(e)}"
            )
    
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", ajuda))
    app.add_handler(CommandHandler("obras", obras))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.VOICE, processar_audio))
    
    print("=" * 60)
    print("🤖 BOT DO TELEGRAM V4.0 CLOUD INICIADO!")
    print("=" * 60)
    print("\n✅ Bot funcionando na nuvem!")
    print("☁️ Hospedagem: 24h ligado")
    print("📊 Armazenamento: Google Planilhas")
    print("🌍 Acesse de qualquer lugar!")
    print("\n⏹️  Para parar, pressione Ctrl+C")
    print("=" * 60)
    print("\n")
    
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Bot encerrado")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")

