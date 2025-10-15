# 🤖 Bot de Controle de Gastos de Construção V4.0

Bot do Telegram para controle de gastos de obras de construção, com salvamento automático no Google Planilhas e hospedagem em nuvem.

## ✨ Recursos

- 🎤 **Controle por voz**: Envie áudios no Telegram
- 🏗️ **Múltiplas obras**: Uma planilha para cada obra
- 📊 **Google Planilhas**: Acesse de qualquer lugar
- ☁️ **Hospedagem em nuvem**: Funciona 24h sem PC ligado
- 💰 **Totais automáticos**: Resumo com valores totais
- 📱 **Multiplataforma**: Acesse pelo celular, tablet ou PC

## 🚀 Como Funciona

1. Você envia um áudio no Telegram mencionando a obra e o gasto
2. O bot transcreve e identifica as informações
3. Salva automaticamente na planilha do Google
4. Você acessa a planilha de qualquer lugar!

## 📋 Exemplo de Uso

**Áudio:** "Comprei 50 sacos de cimento por 1500 reais para a obra do João"

**Bot registra:**
- Obra: João
- Data: Hoje
- Descrição: 50 sacos de cimento
- Categoria: Materiais
- Valor: R$ 1.500,00

## 🛠️ Tecnologias

- Python 3.11
- python-telegram-bot
- gspread (Google Sheets API)
- OpenAI Whisper (transcrição de áudio)
- GPT-4.1-mini (extração de informações)

## 📦 Instalação

Veja o guia completo em: [GUIA_COMPLETO_V4.md](GUIA_COMPLETO_V4.md)

### Resumo:

1. Configurar Google Cloud
2. Fazer deploy no Railway
3. Configurar variáveis de ambiente
4. Testar!

## 🔧 Variáveis de Ambiente

```
TELEGRAM_BOT_TOKEN=seu_token_do_telegram
OPENAI_API_KEY=sua_chave_da_openai
GOOGLE_CREDENTIALS_JSON={"type":"service_account",...}
```

## 📊 Estrutura das Planilhas

Cada obra tem 3 abas:

1. **Gastos**: Data, Descrição, Categoria, Valor, Observações
2. **Pagamentos**: Data, Nome, Função, Valor, Observações
3. **Resumo**: Totais automáticos

## 💰 Custos

- **Google Cloud**: Grátis (dentro dos limites)
- **Railway**: ~R$ 20-30/mês
- **OpenAI API**: Conforme uso (transcrição + análise)

## 📱 Comandos do Bot

- `/start` - Iniciar e ver instruções
- `/obras` - Listar todas as obras (com links!)
- `/ajuda` - Ver exemplos de uso
- `/status` - Ver status do sistema

## 🎯 Dicas de Uso

**Para PAGAMENTOS:**
- "Paguei o pedreiro João 350 reais"
- "Pagamento do ajudante, 200 reais"
- "Mão de obra entrou 300 reais"

**Para GASTOS:**
- "Comprei cimento por 200 reais"
- "Gastei 150 em areia"
- "Materiais diversos, 300 reais"

## 📖 Documentação

- [Guia Completo](GUIA_COMPLETO_V4.md) - Passo a passo detalhado
- [Guia Rápido](GUIA_RAPIDO_V4.txt) - Resumo dos passos

## 🤝 Contribuindo

Este é um projeto pessoal, mas sugestões são bem-vindas!

## 📄 Licença

MIT License - Use à vontade!

## 🏗️ Autor

Desenvolvido com assistência da Manus AI

---

**Versão:** 4.0  
**Data:** 14/10/2025  
**Status:** ✅ Funcionando

