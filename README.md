# 🛰️ Social Sentinel

> **Automated Content Intelligence Platform** — Detect viral hooks, track trending niches, and generate optimized social media content for LinkedIn, X (Twitter), and Threads.

---

<div align="center">

[🇬🇧 English](#-english) · [🇫🇷 Français](#-français)

</div>

---

## 🇬🇧 English

### 📁 Architecture

```
social_sentinel/
├── config.py                  # Centralized configuration (env vars, thresholds)
├── main.py                    # Pipeline orchestrator + CLI entry point
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore rules
├── TUTORIAL.md                # Step-by-step testing guide
├── core/
│   ├── __init__.py
│   ├── scraper.py             # Social media scraping (Apify + mock fallback)
│   └── analyzer.py            # AI analysis engine (GPT-4o) + content generation
├── storage/
│   ├── __init__.py
│   └── hook_bank.py           # SQLite + JSON storage with cosine similarity dedup
├── ui/
│   ├── __init__.py
│   └── dashboard.py           # Streamlit interactive dashboard
└── data/
    ├── hook_bank.db           # SQLite database (auto-created)
    ├── hook_bank.json         # JSON export (auto-synced)
    └── sentinel.log           # Pipeline execution logs
```

### 🚀 Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 3. Run pipeline (mock data by default — no API needed to test)
python -m social_sentinel.main

# 4. Launch dashboard
streamlit run social_sentinel/ui/dashboard.py
```

### 🔧 How It Works

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   SCRAPE     │────▶│   ANALYZE    │────▶│    STORE     │────▶│   GENERATE   │
│ • Apify API  │     │ • GPT-4o     │     │ • SQLite     │     │ • LinkedIn   │
│ • Mock data  │     │ • Hook extract│    │ • Dedup      │     │ • X/Twitter  │
│ • Engagement │     │ • Pattern ID │     │ • JSON sync  │     │ • Vibe tone  │
│   filtering  │     │ • Niche score│     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

### 📊 Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Multi-platform scraping** | ✅ | Apify actors for X, LinkedIn, Threads + mock data fallback |
| **AI-powered analysis** | ✅ | GPT-4o hook extraction, pattern classification, niche scoring |
| **Heuristic fallback** | ✅ | Works without OpenAI API — keyword-based analysis |
| **Hook Bank storage** | ✅ | SQLite + JSON with MD5 + cosine similarity deduplication |
| **Content generation** | ✅ | Optimized posts for LinkedIn & X with Vibe Coding tone |
| **Streamlit dashboard** | ✅ | 4-tab interactive UI with charts and export |
| **CLI interface** | ✅ | `--platform`, `--no-generate`, `--quiet` flags |
| **Trending niches** | ✅ | Aggregate scoring with bar chart visualization |

### 📊 Monitored Keywords

| Category | Keywords |
|----------|----------|
| AI Agents | "AI Agents", "agentic workflows", "autonomous agents" |
| Vibe Coding | "Vibe Coding", "AI coding assistant" |
| LLM Ops | "LLM monitoring", "AI infrastructure" |
| Automation | "AI Automation" |

### 🏗️ Scaling to SaaS

**Phase 1 → MVP (Current):** Single-user CLI + local dashboard, SQLite storage.

**Phase 2 → Multi-User:** FastAPI backend, PostgreSQL, Celery + Redis for scheduled runs, Stripe subscriptions.

**Phase 3 → Full SaaS:** Load-balanced architecture, React/Next.js frontend, dedicated scraping infrastructure.

**Pricing Tiers:**
| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | 50 hooks/month, 1 niche, basic dashboard |
| Pro | $29/mo | 500 hooks/month, all niches, content generation, CSV export |
| Agency | $99/mo | Unlimited hooks, multi-account, API access, white-label |
| Enterprise | Custom | Dedicated scraping, custom keywords, SLA |

---

## 🇫🇷 Français

### 🛰️ Qu'est-ce que Social Sentinel ?

Social Sentinel est une **plateforme d'intelligence de contenu automatisée** qui :

1. **Surveille** les tendances sur LinkedIn, X (Twitter) et Threads dans les niches Tech/IA
2. **Extrait** les structures de "hooks" (accroches) les plus performantes
3. **Analyse** chaque post viral avec l'IA (GPT-4o) pour identifier le pattern, la niche et le score de potentiel
4. **Stocke** les hooks uniques dans une base de données avec dédoublonnage intelligent
5. **Génère** des posts optimisés prêts à publier, adaptés au ton "Vibe Coding"

### 🚀 Démarrage Rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer les clés API
cp .env.example .env
# Éditer .env avec votre OPENAI_API_KEY

# 3. Lancer le pipeline (mode mock par défaut — aucune API requise pour tester)
python -m social_sentinel.main

# 4. Ouvrir le dashboard
streamlit run social_sentinel/ui/dashboard.py
```

### 🔧 Fonctionnalités Détaillées

#### Module d'Extraction (Scraping)
- **Production** : Utilise les acteurs Apify pour chaque plateforme
  - X/Twitter : `quacker/twitter-scraper`
  - LinkedIn : `data-slayer/linkedin-post-analytics-scraper`
  - Threads : `automation-lab/threads-scraper`
- **Développement** : Générateur de données mock réalistes inclus
- **Filtrage** par taux d'engagement : `likes + (reposts × 2)` avec seuil configurable

#### Moteur d'Analyse IA
- **Extraction structurée** via GPT-4o avec format JSON
- **Classification des patterns** : Liste, Contre-intuitif, Storytelling, FOMO, How-To, Hot Take, Data-Driven
- **Score de niche** : Note de 1 à 10 sur la rentabilité/viralité potentielle
- **Fallback heuristique** : Fonctionne SANS API OpenAI — analyse basée sur des mots-clés

#### Banque de Hooks (Hook Bank)
- **Double stockage** : SQLite (primaire) + JSON (export)
- **Dédoublonnage intelligent** : Hash MD5 + similarité cosinus (seuil : 0.85)
- **Détection de niches tendances** : Score agrégé par niche
- **Sync automatique** vers JSON à chaque écriture

#### Génération de Contenu
- Posts optimisés pour **LinkedIn** (150-300 mots) et **X/Twitter** (200-280 caractères)
- Ton : Moderne, technique mais accessible, axé efficacité (style Vibe Coding)
- S'inspire des meilleurs hooks détectés pour créer du contenu original

#### Dashboard Streamlit
- **4 onglets** : Dashboard, Hook Bank, Niches Tendances, Générateur de Contenu
- **Graphiques** : Bar chart des scores par niche
- **Export** : Téléchargement des posts générés en `.txt`
- **Filtres** : Par niche, par plateforme

### 📊 Mots-clés Surveillés

| Catégorie | Mots-clés |
|-----------|-----------|
| Agents IA | "AI Agents", "agentic workflows", "autonomous agents" |
| Vibe Coding | "Vibe Coding", "AI coding assistant" |
| LLM Ops | "LLM monitoring", "AI infrastructure" |
| Automatisation | "AI Automation" |

*Ajoutez vos propres mots-clés dans `config.py` → `ScrapingConfig.keywords`*

### 🏗️ Scaler en Produit SaaS

**Phase 1 → MVP (Actuel) :** CLI mono-utilisateur + dashboard local, stockage SQLite.

**Phase 2 → Multi-Utilisateur :** Backend FastAPI, PostgreSQL, Celery + Redis pour les exécutions planifiées, abonnements Stripe.

**Phase 3 → SaaS Complet :** Architecture load-balancée, frontend React/Next.js, infrastructure de scraping dédiée.

**Grille Tarifaire :**
| Plan | Prix | Fonctionnalités |
|------|------|-----------------|
| Gratuit | 0€ | 50 hooks/mois, 1 niche, dashboard basique |
| Pro | 29€/mois | 500 hooks/mois, toutes niches, génération de contenu, export CSV |
| Agency | 99€/mois | Hooks illimités, multi-comptes, accès API, marque blanche |
| Enterprise | Sur devis | Scraping dédié, mots-clés personnalisés, SLA |

### 📖 Tutoriel Complet

Consultez le fichier [`TUTORIAL.md`](TUTORIAL.md) pour un guide pas-à-pas détaillé avec captures d'écran et exemples concrets.

---

## 📝 License

MIT License — utilisez, modifiez et commercialisez librement.
