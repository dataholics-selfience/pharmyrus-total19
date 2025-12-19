# 🕷️ Pharmyrus V5.3 CRAWLER

**PRÓPRIO CRAWLER - SEM SerpAPI!**

## ✨ O QUE MUDOU

### ❌ ANTES (V5.0-5.2)
- Dependia de SerpAPI ($$$)
- Engine `google_patents` não retornava WO numbers
- Engine `google` não tinha WO nos snippets
- **Resultado: 0 WO numbers, 0 BR patents**

### ✅ AGORA (V5.3)
- **Crawler PRÓPRIO** fazendo HTTP direto em `patents.google.com`
- **BeautifulSoup** para parsing HTML
- **Regex** para extração de WO e BR numbers
- **SEM custo de API externa**

---

## 🔧 COMO FUNCIONA

### 1. WO Discovery
```python
# Acessa direto patents.google.com
GET https://patents.google.com/?q=Darolutamide

# Parse HTML com BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Extrai WO de links: /patent/WO2011104180A1
# Extrai WO de texto via regex: WO 2011/104180
```

### 2. BR from WO Families
```python
# Acessa página do WO
GET https://patents.google.com/patent/WO2011104180

# Busca links para BR patents: /patent/BR112018068911A2
# Extrai BR numbers do HTML
```

### 3. Direct BR Search
```python
# Busca direta por BR
GET https://patents.google.com/?q=Darolutamide+BR&country=BR

# Extrai todos BR patents da página
```

---

## 🚀 DEPLOY

### 1. Commit
```bash
unzip pharmyrus-v5-CRAWLER.zip
cd pharmyrus-v5-CRAWLER

git init
git add .
git commit -m "feat: V5.3 - Own crawler, no SerpAPI dependency"
git push
```

### 2. Railway
**DELETE projeto antigo → New Project → Deploy from GitHub**

### 3. Test
```bash
POST https://SEU-APP.railway.app/api/v5/search

{
  "molecule_name": "Darolutamide",
  "brand_name": "Nubeqa"
}
```

---

## 📊 RESPONSE ESPERADA

```json
{
  "molecule_info": {
    "name": "Darolutamide",
    "cid": 67171867,
    "dev_codes": ["ODM-201", "BAY-1841788"]
  },
  "search_strategy": {
    "mode": "direct_crawler",
    "sources": [
      "PubChem",
      "Google Patents Crawler",
      "INPI Crawler"
    ],
    "note": "No SerpAPI - direct HTTP scraping"
  },
  "wo_processing": {
    "total_wo_found": 8-15,
    "wo_numbers": ["WO2011104180", "WO2016128449", ...],
    "wo_processed": 10
  },
  "summary": {
    "total_br_patents": 10-14,
    "from_inpi": 5-8,
    "from_google_wo": 3-5,
    "from_google_direct": 2-4
  },
  "br_patents": [
    {
      "publication_number": "BR112018068911A2",
      "title": "...",
      "source": "google_crawler_wo_WO2011104180",
      "score": 8
    },
    ...
  ],
  "comparison": {
    "expected": 8,
    "found": 12,
    "match_rate": "150%",
    "status": "✅ Excellent"
  },
  "execution_time": 45-70
}
```

---

## ⚡ VANTAGENS

✅ **Zero custo** - Sem SerpAPI
✅ **Controle total** - Nosso próprio código
✅ **Mais resultados** - Acesso direto ao HTML
✅ **Debugging fácil** - Logs detalhados
✅ **Escalável** - Podemos otimizar à vontade

---

## 🛠️ TECNOLOGIAS

- **BeautifulSoup4**: HTML parsing
- **requests**: HTTP client
- **regex**: Pattern extraction
- **FastAPI**: API framework
- **INPI Crawler**: Railway endpoint

---

## 📝 ESTRUTURA

```
pharmyrus-v5-CRAWLER/
├── app/
│   ├── main.py
│   ├── services/
│   │   ├── google_crawler.py  ← NOVO! Crawler próprio
│   │   ├── pubchem.py
│   │   ├── inpi.py
│   │   └── orchestrator.py
│   └── models/
│       └── patent.py
├── requirements.txt            ← BeautifulSoup4 + lxml
├── Dockerfile
└── README.md
```

---

**Versão**: 5.3.0 CRAWLER  
**Status**: Own crawler - No SerpAPI  
**Expected**: 10-14 BR patents in 45-70s
