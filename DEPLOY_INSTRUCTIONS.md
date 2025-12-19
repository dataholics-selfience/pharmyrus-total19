# 🚨 INSTRUÇÕES CRÍTICAS DE DEPLOY NO RAILWAY

## ⚠️ PROBLEMA IDENTIFICADO

O Railway está usando **Docker image em CACHE antiga** que contém o bug do `$PORT`.

## ✅ SOLUÇÃO: FORÇAR REBUILD COMPLETO

### Opção 1: Delete o Projeto e Recrie (RECOMENDADO)

1. **Railway Dashboard** → Seu projeto atual
2. **Settings** → **Danger Zone** → **Delete Project**
3. Confirme a exclusão
4. **New Project** → **Deploy from GitHub** → Selecione o repo
5. Railway vai fazer build LIMPO do zero ✅

### Opção 2: Trigger Manual Rebuild

1. **Railway Dashboard** → Seu projeto
2. **Deployments** → Click no último deploy
3. **⋮** (três pontinhos) → **Re-deploy** 
4. ⚠️ Pode não funcionar se estiver usando cache!

### Opção 3: Force Push com Commit Vazio

```bash
git commit --allow-empty -m "Force Railway rebuild - clear Docker cache"
git push origin main
```

## 🔍 VERIFICAR SE O BUG FOI CORRIGIDO

### Logs CORRETOS (após fix):
```
Building...
Successfully built image
Starting Container
INFO: Started server process [1]
🚀 Pharmyrus V5.0 Starting...
   Port: 45612        ← NÚMERO, não "$PORT"!
INFO: Uvicorn running on http://0.0.0.0:45612
Starting Healthcheck
Healthcheck Successful!
```

### Logs ERRADOS (bug ainda presente):
```
Starting Container
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## 📋 CHECKLIST PRÉ-DEPLOY

- [ ] Código committed no GitHub
- [ ] Dockerfile tem `${PORT:-8000}` SEM quotes
- [ ] railway.json existe
- [ ] requirements.txt completo
- [ ] app/main.py tem endpoint /health
- [ ] .gitignore configurado

## 🎯 DOCKERFILE CORRETO

```dockerfile
# CORRETO ✅
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
#                                                   ↑ SEM QUOTES!

# ERRADO ❌
CMD uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
#                                                   ↑ COM QUOTES = BUG!
```

## 🧪 TESTE LOCAL ANTES DO DEPLOY

```bash
# Build Docker local
docker build -t pharmyrus-test .

# Rodar com PORT variável
docker run -e PORT=8000 -p 8000:8000 pharmyrus-test

# Testar health check
curl http://localhost:8000/health

# Deve retornar:
# {"status":"healthy","version":"5.0.0",...}
```

## 📞 SE CONTINUAR COM ERRO

1. **Delete o projeto Railway completamente**
2. **Limpe o cache do GitHub** (Settings → Actions → Clear cache)
3. **Force push novo commit**:
   ```bash
   git commit --allow-empty -m "chore: force complete rebuild"
   git push --force origin main
   ```
4. **Crie novo projeto Railway do zero**

## ⏱️ TEMPO ESPERADO

- Build: 2-3 minutos
- Deploy: 30-60 segundos  
- Health check: 10-30 segundos
- **Total: ~5 minutos**

Se passar de 5 minutos, algo está errado!

---

**LEMBRE-SE**: O bug do `$PORT` vem do DOCKER IMAGE EM CACHE.  
A única solução garantida é **DELETE + RECRIE o projeto Railway**! 🔥
