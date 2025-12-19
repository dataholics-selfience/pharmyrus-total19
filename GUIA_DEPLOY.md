# 🎯 GUIA DE DEPLOY - PASSO A PASSO

## ✅ PROBLEMA RESOLVIDO

O erro `'$PORT' is not a valid integer` foi causado por:
1. Railway estava usando imagem Docker cacheada antiga
2. Script de entrypoint tinha quotes no $PORT

## 🆕 SOLUÇÃO IMPLEMENTADA

Projeto **COMPLETAMENTE NOVO** com:
- ✅ Dockerfile otimizado SEM entrypoint script
- ✅ CMD direto usando `${PORT:-8000}` (expansão correta)
- ✅ FastAPI production-ready
- ✅ Health check configurado
- ✅ railway.json com configurações corretas

---

## 📤 DEPLOY PASSO A PASSO

### 1️⃣ Preparar Repositório GitHub

```bash
# Navegue até a pasta do projeto
cd pharmyrus-v5-railway

# Inicialize o Git
git init

# Adicione todos os arquivos
git add .

# Primeiro commit
git commit -m "feat: Pharmyrus V5.0 production ready for Railway"

# Crie repositório no GitHub
# Vá em: https://github.com/new
# Nome: pharmyrus-v5
# Deixe público ou privado (Railway funciona em ambos)

# Conecte ao repositório remoto (substitua YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/pharmyrus-v5.git

# Push para GitHub
git branch -M main
git push -u origin main
```

### 2️⃣ Deploy no Railway

#### Opção A: Via Dashboard (RECOMENDADO)

1. Acesse: https://railway.app/dashboard

2. **Delete o projeto antigo com problemas**:
   - Clique em "efficient-happiness"
   - Settings → Danger Zone → Delete Project
   - Confirme a exclusão

3. **Crie novo projeto**:
   - Click "New Project"
   - Selecione "Deploy from GitHub repo"
   - Escolha o repositório: `pharmyrus-v5`
   - Railway detectará automaticamente o Dockerfile
   - Click "Deploy Now"

4. **Aguarde o build**:
   - Build leva ~2-3 minutos
   - Acompanhe os logs em tempo real

5. **Obtenha a URL**:
   - Vá em "Settings" → "Networking"
   - Click "Generate Domain"
   - URL será algo como: `pharmyrus-v5-production.up.railway.app`

#### Opção B: Via Railway CLI

```bash
# Instale Railway CLI (se não tiver)
curl -fsSL https://railway.app/install.sh | sh

# Faça login
railway login

# Crie novo projeto
railway init

# Deploy
railway up

# Obtenha URL
railway domain
```

### 3️⃣ Verificar Deploy

```bash
# Teste health endpoint
curl https://SEU-APP.railway.app/health

# Resposta esperada:
{
  "status": "healthy",
  "version": "5.0.0",
  "timestamp": "2025-12-19T14:30:00.000Z",
  "port": 12345
}
```

### 4️⃣ Testar API

```bash
# Abra no navegador:
https://SEU-APP.railway.app/docs

# Ou teste via curl:
curl -X POST https://SEU-APP.railway.app/api/v5/search \
  -H "Content-Type: application/json" \
  -d '{
    "nome_molecula": "Darolutamide",
    "pais_alvo": "BR"
  }'
```

---

## 🔍 LOGS ESPERADOS

### ✅ Build Bem-sucedido

```
Building...
#1 [internal] load build definition from Dockerfile
#2 [internal] load .dockerignore
#3 [internal] load metadata for docker.io/library/python:3.11-slim
...
#10 DONE 45.2s
Building pharmyrus-v5-railway:latest
Successfully built image
Image size: 280 MB
```

### ✅ Container Iniciando

```
Starting Container
INFO:     Started server process [1]
INFO:     Waiting for application startup.
============================================================
🚀 Pharmyrus V5.0 Starting...
   Environment: production
   Port: 45612
   Version: 5.0.0
============================================================
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:45612 (Press CTRL+C to quit)
```

### ✅ Healthcheck Passando

```
Starting Healthcheck - Path: /health
Healthcheck attempt 1/3...
Healthcheck Successful!
```

---

## ❌ SE AINDA DER ERRO

### Problema: Build Falha

```bash
# Verifique se todos os arquivos estão no repo
git status

# Deve mostrar tudo commitado
# nothing to commit, working tree clean
```

### Problema: Container Não Inicia

```bash
# Veja logs completos
railway logs --tail 200

# Busque por erros específicos
railway logs | grep -i "error"
```

### Problema: Healthcheck Falha

```bash
# Verifique se porta está correta
railway variables

# PORT deve estar vazio (Railway injeta automaticamente)
# Se tiver valor manual, delete:
railway variables delete PORT
```

---

## 📊 ESTRUTURA DO PROJETO

```
pharmyrus-v5-railway/
├── app/
│   └── main.py              # 🎯 Aplicação FastAPI
├── Dockerfile               # 🐳 Build otimizado
├── requirements.txt         # 📦 Dependências Python
├── railway.json            # ⚙️  Config Railway
├── .gitignore              # 🚫 Arquivos ignorados
├── README.md               # 📖 Documentação
├── test-local.sh           # 🧪 Teste local
└── GUIA_DEPLOY.md          # 📋 Este arquivo
```

---

## ✅ CHECKLIST FINAL

Antes de dar push:
- [ ] Todos os arquivos criados e salvos
- [ ] Git init executado
- [ ] Primeiro commit feito
- [ ] Repositório GitHub criado
- [ ] Remote origin configurado
- [ ] Push para GitHub bem-sucedido

Deploy Railway:
- [ ] Projeto antigo deletado (se houver)
- [ ] Novo projeto criado a partir do GitHub
- [ ] Build completou sem erros
- [ ] Container iniciou com sucesso
- [ ] Healthcheck passou
- [ ] URL gerada e acessível

Testes:
- [ ] `/health` retorna status healthy
- [ ] `/docs` abre interface Swagger
- [ ] `/api/v5/search` aceita requisições

---

## 🎉 SUCESSO!

Quando tudo estiver funcionando, você verá:

```
✅ Build: Success
✅ Deploy: Active
✅ Health: Passing
✅ Status: Healthy
```

**URL da API**: https://seu-app.railway.app

---

**IMPORTANTE**: Este é um projeto **NOVO E LIMPO**. 

Não tente atualizar o projeto antigo - delete e crie novo!

Railway vai buildar do zero sem cache antigo.

**BOA SORTE! 🚀**
