# 📘 Social Sentinel — Tutoriel de Test Complet

Ce guide pas-à-pas vous permet de tester **toutes les fonctionnalités** de Social Sentinel, du mode mock (sans API) jusqu'au déploiement complet avec OpenAI et Apify.

---

## 📋 Prérequis

- **Python 3.10+** installé
- **pip** (gestionnaire de paquets Python)
- **OpenAI API key** (optionnel — pour l'analyse IA complète)
- **Apify API key** (optionnel — pour le scraping réel)

---

## Étape 1 : Installation

```bash
# Se placer dans le dossier du projet
cd social_sentinel

# Créer un environnement virtuel (recommandé)
python -m venv venv

# Activer l'environnement
# Windows :
venv\Scripts\activate
# macOS/Linux :
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

**Vérification :**
```bash
pip list | grep -E "openai|streamlit|python-dotenv"
```
Vous devez voir les 3 paquets listés.

---

## Étape 2 : Configuration (Mode Test — Sans API)

Par défaut, Social Sentinel fonctionne en **mode mock** — aucune clé API n'est nécessaire.

```bash
# Copier le fichier d'exemple
cp .env.example .env

# Le fichier .env par défaut a déjà USE_MOCK_DATA=true
# Rien à modifier pour le test initial
```

---

## Étape 3 : Premier Test — Pipeline Complet

```bash
python -m social_sentinel.main
```

**Ce qui se passe :**
1. ✅ 20 posts mock sont générés (réalistes avec auteurs, engagement, niches)
2. ✅ Chaque post est analysé (fallback heuristique sans API OpenAI)
3. ✅ Les hooks uniques sont stockés dans `data/hook_bank.db`
4. ✅ Un post optimisé LinkedIn est généré (template fallback)
5. ✅ Un rapport complet s'affiche dans la console

**Sortie attendue :**
```
============================================================
📊 SOCIAL SENTINEL - DAILY REPORT
============================================================

📈 Hook Bank Stats:
   Total Hooks: 20
   Unique Niches: 8
   Avg Niche Score: 7.5/10

🔥 Trending Niches:
   1. AI Agents (Score: 8.2, 5 hooks)
   2. Vibe Coding (Score: 7.8, 4 hooks)
   ...

🏆 Top Hook of the Day:
   "I spent 100 hours building AI agents..."
   Pattern: Storytelling | Niche: AI Agents | Score: 9/10

📝 Generated Post (ready to publish):
------------------------------------------------
🚀 The AI landscape is shifting faster than ever.
...
------------------------------------------------
```

---

## Étape 4 : Tester avec l'API OpenAI (Analyse IA Réelle)

Pour une analyse IA complète avec GPT-4o :

```bash
# Éditer .env
# Remplacer sk-your-key-here par votre vraie clé OpenAI
OPENAI_API_KEY=sk-proj-votre-vraie-cle

# Relancer le pipeline
python -m social_sentinel.main
```

**Différence :** Au lieu du fallback heuristique, GPT-4o analyse chaque post et extrait :
- Le hook exact
- Le type de pattern (Storytelling, FOMO, Hot Take, etc.)
- La niche spécifique
- Le score de potentiel (1-10)
- Le trigger émotionnel
- La raison de la viralité

---

## Étape 5 : Tester le Dashboard Streamlit

```bash
streamlit run social_sentinel/ui/dashboard.py
```

Le dashboard s'ouvre dans votre navigateur (`http://localhost:8501`) avec **4 onglets** :

### Onglet 1 — 📊 Dashboard
- Vue d'ensemble du pipeline
- Bouton "Run Pipeline" pour lancer une nouvelle analyse
- Métriques : Posts scrapés, Hooks ajoutés, Total en banque
- Post généré affiché avec bouton de téléchargement

### Onglet 2 — 🏆 Hook Bank
- Liste de tous les hooks collectés
- Filtre par niche
- Chaque hook est expandable pour voir : pattern, niche, plateforme, auteur, trigger émotionnel
- Indicateur 🔥 (score ≥ 8) ou ⭐ (score < 8)

### Onglet 3 — 🔥 Trending Niches
- Classement des niches par score moyen
- Graphique en barres comparant avg_score vs max_score
- Métriques : nombre de hooks, score moyen, score maximum

### Onglet 4 — 📝 Content Generator
- Sélection de la plateforme (LinkedIn ou X)
- Niche cible optionnelle
- Bouton "Generate Post" pour créer un nouveau post
- Téléchargement ou copie du post généré

---

## Étape 6 : Tester les Options CLI

```bash
# Générer un post pour X/Twitter au lieu de LinkedIn
python -m social_sentinel.main --platform twitter

# Uniquement scraper + analyser + stocker (sans génération)
python -m social_sentinel.main --no-generate

# Mode silencieux (pas de rapport console, juste les logs)
python -m social_sentinel.main --quiet

# Combiner les options
python -m social_sentinel.main --platform twitter --no-generate
```

---

## Étape 7 : Vérifier les Données Stockées

```bash
# Voir le fichier JSON exporté
cat data/hook_bank.json

# Voir les logs d'exécution
cat data/sentinel.log
```

---

## Étape 8 : Activer le Scraping Réel (Optionnel)

Pour passer du mode mock au scraping réel :

```bash
# 1. Obtenir une clé API Apify sur https://apify.com
# 2. Éditer .env :
APIFY_API_KEY=apify_api_votre_cle
USE_MOCK_DATA=false

# 3. Relancer
python -m social_sentinel.main
```

⚠️ **Attention** : Le scraping réel consomme des crédits Apify. Commencez avec peu de mots-clés.

---

## 🧪 Checklist de Vérification

Testez chaque fonctionnalité et cochez :

- [ ] **Pipeline mock** : `python -m social_sentinel.main` fonctionne sans erreur
- [ ] **Rapport console** : Affiche stats, niches tendances, top hook, post généré
- [ ] **Hook Bank DB** : Le fichier `data/hook_bank.db` est créé
- [ ] **Hook Bank JSON** : Le fichier `data/hook_bank.json` contient les hooks
- [ ] **Logs** : Le fichier `data/sentinel.log` existe et contient les logs
- [ ] **Dashboard** : `streamlit run` ouvre l'interface avec 4 onglets
- [ ] **Dédoublonnage** : Relancer le pipeline 2x — les doublons sont rejetés
- [ ] **CLI options** : `--platform twitter`, `--no-generate`, `--quiet` fonctionnent
- [ ] **OpenAI** (si clé configurée) : Analyse IA réelle avec GPT-4o
- [ ] **Post généré** : Le contenu est cohérent et prêt à publier

---

## 🐛 Dépannage

### `ImportError: No module named 'social_sentinel'`
```bash
# S'assurer d'être DANS le dossier parent (pas dans social_sentinel/)
cd ..
python -m social_sentinel.main
```

### `ModuleNotFoundError: No module named 'dotenv'`
```bash
pip install python-dotenv
```

### `streamlit: command not found`
```bash
pip install --upgrade streamlit
```

### Le dashboard ne charge pas les hooks
```bash
# Vérifier que le pipeline a bien été lancé avant
python -m social_sentinel.main
# Puis relancer le dashboard
streamlit run social_sentinel/ui/dashboard.py
```

### Erreur OpenAI API
```bash
# Vérifier la clé dans .env
cat .env | grep OPENAI_API_KEY
# Le fallback heuristique s'active automatiquement en cas d'erreur
```

---

## 🎯 Prochaines Étapes

1. **Personnaliser les mots-clés** dans `config.py`
2. **Ajuster le seuil d'engagement** (`min_engagement_score`)
3. **Modifier les templates** de génération dans `analyzer.py`
4. **Déployer le dashboard** sur Streamlit Cloud (gratuit)
5. **Configurer un cron** pour des exécutions automatiques
