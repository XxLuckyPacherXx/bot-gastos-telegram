# 🚀 Guia Completo - Bot V4.0 na Nuvem com Google Planilhas

## 📋 Visão Geral

A Versão 4.0 traz:
- ✅ Bot rodando na nuvem (24h ligado)
- ✅ Salvando no Google Planilhas
- ✅ Sem precisar deixar PC ligado
- ✅ Acesso de qualquer lugar (celular, tablet, PC)
- ✅ Backup automático na nuvem

---

## 🎯 O Que Você Vai Fazer

1. **Configurar Google Cloud** (~15 minutos)
2. **Fazer Deploy no Railway** (~10 minutos)
3. **Testar o Bot** (~5 minutos)

**Total: ~30 minutos**

---

## 📦 PARTE 1: Configurar Google Cloud

### Passo 1: Criar Projeto no Google Cloud

1. Acesse: https://console.cloud.google.com/
2. Faça login com sua conta Google
3. Clique em **"Selecionar projeto"** (canto superior)
4. Clique em **"NOVO PROJETO"**
5. Nome do projeto: `bot-gastos-construcao`
6. Clique em **"CRIAR"**
7. Aguarde a criação (uns 30 segundos)

### Passo 2: Ativar Google Sheets API

1. No menu lateral, vá em: **APIs e Serviços** → **Biblioteca**
2. Pesquise: `Google Sheets API`
3. Clique no resultado
4. Clique em **"ATIVAR"**
5. Aguarde ativar

### Passo 3: Ativar Google Drive API

1. Ainda na Biblioteca de APIs
2. Pesquise: `Google Drive API`
3. Clique no resultado
4. Clique em **"ATIVAR"**
5. Aguarde ativar

### Passo 4: Criar Conta de Serviço

1. No menu lateral: **APIs e Serviços** → **Credenciais**
2. Clique em **"CRIAR CREDENCIAIS"**
3. Selecione: **"Conta de serviço"**
4. Preencha:
   - **Nome:** `bot-telegram-gastos`
   - **ID:** (deixa o que aparecer automaticamente)
   - **Descrição:** `Bot do Telegram para controle de gastos`
5. Clique em **"CRIAR E CONTINUAR"**
6. Em "Conceder acesso ao projeto":
   - **Função:** Selecione `Editor`
7. Clique em **"CONTINUAR"**
8. Clique em **"CONCLUIR"**

### Passo 5: Gerar Chave JSON

1. Na lista de Contas de Serviço, clique na que você criou
2. Vá na aba **"CHAVES"**
3. Clique em **"ADICIONAR CHAVE"** → **"Criar nova chave"**
4. Selecione tipo: **JSON**
5. Clique em **"CRIAR"**
6. Um arquivo JSON será baixado automaticamente
7. **GUARDE ESTE ARQUIVO!** Você vai precisar dele!

### Passo 6: Copiar Email da Conta de Serviço

1. Ainda na página da Conta de Serviço
2. Copie o **email** que aparece (algo como: `bot-telegram-gastos@...iam.gserviceaccount.com`)
3. **GUARDE ESTE EMAIL!** Você vai usar para compartilhar planilhas

---

## 🚂 PARTE 2: Deploy no Railway

### Passo 1: Criar Conta no Railway

1. Acesse: https://railway.app/
2. Clique em **"Login"**
3. Faça login com GitHub (recomendado) ou email
4. Se não tem GitHub, crie uma conta gratuita em: https://github.com/

### Passo 2: Criar Novo Projeto

1. No Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Se for a primeira vez, autorize o Railway a acessar seu GitHub
4. Clique em **"Configure GitHub App"**
5. Selecione **"All repositories"** ou escolha um repositório específico

**IMPORTANTE:** Você precisa subir o código para o GitHub primeiro!

---

## 📤 PARTE 2.1: Subir Código para GitHub

### Opção A: Usando GitHub Desktop (Mais Fácil)

1. Baixe e instale: https://desktop.github.com/
2. Faça login com sua conta GitHub
3. Clique em **"Create a New Repository"**
4. Nome: `bot-gastos-telegram`
5. Local Path: Escolha a pasta onde você salvou os arquivos do bot
6. Clique em **"Create Repository"**
7. Clique em **"Publish repository"**
8. Desmarque **"Keep this code private"** (ou deixe marcado se quiser privado)
9. Clique em **"Publish Repository"**

### Opção B: Usando Git na Linha de Comando

```bash
# Na pasta do bot
git init
git add .
git commit -m "Bot v4.0 - Primeira versão"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/bot-gastos-telegram.git
git push -u origin main
```

---

## 🚂 PARTE 2.2: Continuar Deploy no Railway

### Passo 3: Selecionar Repositório

1. No Railway, selecione o repositório que você criou
2. Railway vai detectar automaticamente que é um projeto Python
3. Clique em **"Deploy Now"**

### Passo 4: Configurar Variáveis de Ambiente

1. No projeto do Railway, clique na aba **"Variables"**
2. Adicione as seguintes variáveis:

#### Variável 1: TELEGRAM_BOT_TOKEN
- **Key:** `TELEGRAM_BOT_TOKEN`
- **Value:** Cole o token do seu bot do Telegram

#### Variável 2: OPENAI_API_KEY
- **Key:** `OPENAI_API_KEY`
- **Value:** (Já deve estar configurada no ambiente)

#### Variável 3: GOOGLE_CREDENTIALS_JSON
- **Key:** `GOOGLE_CREDENTIALS_JSON`
- **Value:** Abra o arquivo JSON que você baixou do Google Cloud
- Copie TODO o conteúdo do arquivo
- Cole aqui (vai ser um JSON grande)

**IMPORTANTE:** O JSON deve estar em uma linha só, ou copie exatamente como está no arquivo.

### Passo 5: Verificar Deploy

1. Vá na aba **"Deployments"**
2. Aguarde o deploy terminar (uns 2-3 minutos)
3. Se der tudo certo, vai aparecer **"Success"** em verde
4. Vá na aba **"Logs"** para ver se o bot iniciou

Você deve ver algo como:
```
🤖 BOT DO TELEGRAM V4.0 CLOUD INICIADO!
✅ Bot funcionando na nuvem!
```

---

## 🧪 PARTE 3: Testar o Bot

### Passo 1: Enviar Áudio de Teste

1. Abra o Telegram
2. Procure seu bot
3. Envie um áudio: "Comprei cimento por 200 reais para a obra teste"
4. Aguarde a resposta

### Passo 2: Verificar Planilha Criada

1. O bot vai responder com um link da planilha
2. Clique no link
3. **IMPORTANTE:** Na primeira vez, você vai ver um erro de permissão!

### Passo 3: Dar Permissão à Planilha

A planilha foi criada pela conta de serviço, então você precisa se adicionar:

1. Abra o Google Drive: https://drive.google.com/
2. Procure por "Obra: Teste" (ou o nome da obra que você mencionou)
3. Clique com botão direito na planilha
4. Clique em **"Compartilhar"**
5. Adicione seu email pessoal como **"Editor"**
6. Clique em **"Enviar"**

**OU** você pode adicionar seu email diretamente no código (mais prático):

No arquivo `bot_telegram_v4.py`, linha ~184, descomente e adicione seu email:
```python
spreadsheet.share('seu_email@gmail.com', perm_type='user', role='writer')
```

Depois faça commit e push para o GitHub, o Railway vai fazer deploy automático.

### Passo 4: Verificar Dados

1. Abra a planilha
2. Vá na aba **"Gastos"**
3. Deve ter o item que você adicionou
4. Vá na aba **"Resumo"**
5. O total deve aparecer automaticamente!

---

## 💰 PARTE 4: Configurar Pagamento no Railway

### Passo 1: Adicionar Cartão

1. No Railway, clique no seu perfil (canto superior direito)
2. Vá em **"Account Settings"**
3. Clique em **"Billing"**
4. Clique em **"Add Payment Method"**
5. Adicione seu cartão de crédito

### Passo 2: Entender os Custos

Railway cobra por:
- **Uso de CPU/RAM:** ~$0.000463 por GB-hora
- **Estimativa mensal:** ~R$ 20-30 (depende do uso)

**Dica:** Railway oferece $5 de crédito grátis por mês. Se o bot usar pouco, pode até ser grátis!

### Passo 3: Monitorar Uso

1. Em **"Billing"** você vê o uso atual
2. Configure alertas de limite se quiser
3. Pode cancelar a qualquer momento

---

## 🎯 PARTE 5: Usar o Bot no Dia a Dia

### Comandos Disponíveis

- `/start` - Ver boas-vindas e instruções
- `/obras` - Listar todas as obras (com links!)
- `/ajuda` - Ver exemplos de uso
- `/status` - Ver status do sistema

### Dicas de Uso

**Para PAGAMENTOS, fale assim:**
- "Paguei o pedreiro João 350 reais"
- "Pagamento do ajudante, 200 reais"
- "Salário do mestre de obras, 500 reais"
- "Mão de obra entrou 300 reais"

**Para GASTOS, fale assim:**
- "Comprei cimento por 200 reais"
- "Gastei 150 em areia"
- "Materiais diversos, 300 reais"

### Acessar Planilhas

**Pelo Telegram:**
- Use `/obras` para ver links de todas as planilhas

**Pelo Google Drive:**
- Acesse: https://drive.google.com/
- Procure por "Obra: [nome]"
- Abra e edite à vontade!

**Pelo Celular:**
- Instale o app Google Planilhas
- Acesse suas planilhas
- Edite em tempo real!

---

## 🔧 PARTE 6: Manutenção e Troubleshooting

### Ver Logs do Bot

1. No Railway, vá na aba **"Logs"**
2. Veja em tempo real o que o bot está fazendo
3. Se der erro, aparece aqui

### Bot Não Responde

**Verifique:**
1. Railway está rodando? (veja em Deployments)
2. Variáveis de ambiente estão corretas?
3. Tem crédito no Railway?
4. Veja os logs para erros

### Erro de Permissão na Planilha

**Solução:**
1. Abra a planilha no Google Drive
2. Compartilhe com seu email
3. Ou adicione seu email no código (linha 184)

### Atualizar o Bot

1. Faça mudanças no código localmente
2. Commit e push para o GitHub
3. Railway faz deploy automático!

---

## 📊 PARTE 7: Recursos Avançados

### Compartilhar Planilhas com Equipe

1. Abra a planilha no Google Drive
2. Clique em **"Compartilhar"**
3. Adicione emails da sua equipe
4. Escolha permissão: **"Editor"** ou **"Visualizador"**

### Fazer Backup

As planilhas já estão no Google Drive (backup automático!), mas você pode:
1. Baixar como Excel: **Arquivo** → **Fazer download** → **Microsoft Excel**
2. Fazer cópia: **Arquivo** → **Fazer uma cópia**

### Migrar Dados Antigos

Se você tem planilhas Excel antigas:
1. Abra no Google Drive
2. Clique com botão direito
3. **"Abrir com"** → **"Google Planilhas"**
4. Converte automaticamente!

---

## 🎉 Pronto!

Seu bot está funcionando na nuvem com Google Planilhas!

**Vantagens:**
- ✅ Funciona 24h sem PC ligado
- ✅ Acessa de qualquer lugar
- ✅ Backup automático
- ✅ Compartilha com equipe
- ✅ Edita pelo celular

**Custo:** ~R$ 20-30/mês

---

## 📞 Precisa de Ajuda?

Se tiver dúvidas em algum passo, me avise que eu te ajudo!

Boa sorte com seu controle de gastos! 🏗️

