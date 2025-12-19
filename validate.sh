#!/bin/bash
# Validação pré-deploy do Pharmyrus V5.0

echo "🔍 VALIDAÇÃO PRÉ-DEPLOY - Pharmyrus V5.0"
echo "========================================"
echo ""

ERRORS=0

# 1. Verificar arquivos essenciais
echo "📋 Verificando arquivos..."

FILES=(
    "app/main.py"
    "Dockerfile"
    "requirements.txt"
    "railway.json"
    ".gitignore"
    "README.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file - FALTANDO!"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""

# 2. Verificar Dockerfile
echo "🐳 Verificando Dockerfile..."

if grep -q "CMD uvicorn app.main:app" Dockerfile; then
    echo "  ✅ CMD correto encontrado"
else
    echo "  ❌ CMD incorreto no Dockerfile!"
    ERRORS=$((ERRORS + 1))
fi

if grep -q '\${PORT:-8000}' Dockerfile; then
    echo "  ✅ PORT expansion correto"
else
    echo "  ❌ PORT expansion incorreto!"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# 3. Verificar main.py
echo "🐍 Verificando main.py..."

if grep -q "FastAPI" app/main.py; then
    echo "  ✅ FastAPI importado"
else
    echo "  ❌ FastAPI não encontrado!"
    ERRORS=$((ERRORS + 1))
fi

if grep -q "/health" app/main.py; then
    echo "  ✅ Health endpoint definido"
else
    echo "  ❌ Health endpoint não encontrado!"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# 4. Verificar requirements.txt
echo "📦 Verificando requirements.txt..."

REQUIRED_DEPS=("fastapi" "uvicorn" "pydantic")

for dep in "${REQUIRED_DEPS[@]}"; do
    if grep -q "$dep" requirements.txt; then
        echo "  ✅ $dep"
    else
        echo "  ❌ $dep - FALTANDO!"
        ERRORS=$((ERRORS + 1))
    fi
done

echo ""

# 5. Verificar Git
echo "🔧 Verificando Git..."

if [ -d ".git" ]; then
    echo "  ✅ Repositório Git inicializado"
    
    if git remote -v | grep -q "origin"; then
        echo "  ✅ Remote origin configurado"
        git remote -v | head -2
    else
        echo "  ⚠️  Remote origin NÃO configurado"
        echo "     Execute: git remote add origin <URL>"
    fi
else
    echo "  ⚠️  Git NÃO inicializado"
    echo "     Execute: git init"
fi

echo ""

# RESULTADO FINAL
echo "========================================"

if [ $ERRORS -eq 0 ]; then
    echo "✅ VALIDAÇÃO PASSOU!"
    echo ""
    echo "🚀 Pronto para deploy!"
    echo ""
    echo "Próximos passos:"
    echo "  1. git add ."
    echo "  2. git commit -m 'Initial commit'"
    echo "  3. git push origin main"
    echo "  4. Deploy no Railway via Dashboard ou CLI"
    echo ""
    exit 0
else
    echo "❌ VALIDAÇÃO FALHOU!"
    echo ""
    echo "Erros encontrados: $ERRORS"
    echo "Corrija os problemas antes de fazer deploy."
    echo ""
    exit 1
fi
