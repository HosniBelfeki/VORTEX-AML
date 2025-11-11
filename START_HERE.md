# 🚀 VORTEX-AML - START HERE

## ✅ Votre Système est Prêt!

```
┌────────────────────────────────────────────────┐
│  VORTEX-AML                                    │
│  Enterprise Anti-Money Laundering Platform    │
│                                                │
│  Status: 🟢 READY TO USE                      │
│  AI Services: ✅ LandingAI | 📝 Mock Bedrock  │
└────────────────────────────────────────────────┘
```

## 🎯 Démarrage Rapide (30 secondes)

### Étape 1: Vérifier le Status
```bash
python check_services.py
```

### Étape 2: Démarrer l'Application
```bash
start-all.bat
```

### Étape 3: Ouvrir le Frontend
Ouvrez votre navigateur: **http://localhost:3000**

**C'est tout! 🎉**

## 📊 Ce Qui Fonctionne

### ✅ LandingAI (REAL AI)
- Extraction de documents PDF/images
- OCR intelligent
- Détection de champs structurés
- **Status**: WORKING

### 📝 AWS Bedrock (MOCK MODE)
- Analyse de risque
- Génération de recommandations
- Flags de conformité
- **Status**: Mock (intelligent rules)

### 🎨 Frontend React
- Dashboard interactif
- Upload de documents
- Screening manuel
- Analyse CSV en masse
- Gestion des cas
- **Status**: FULLY FUNCTIONAL

## 🔑 Configuration Actuelle

Votre `.env` est configuré avec:

```env
✅ LANDING_AI_API_KEY: Valid
❌ AWS_ACCESS_KEY_ID: Placeholder (using mock)
❌ AWS_SECRET_ACCESS_KEY: Placeholder (using mock)
```

**Résultat**: LandingAI réel + Bedrock mock = **Parfait pour démo!**

## 🎬 Scénarios de Test

### 1. Screening Manuel
1. Allez sur http://localhost:3000/screening
2. Entrez un nom: "Vladimir Putin"
3. Cliquez "Screen Entity"
4. Voir les résultats de risque

### 2. Upload de Document
1. Allez sur http://localhost:3000/upload
2. Uploadez un PDF ou image
3. Voir l'extraction automatique
4. Voir l'analyse de risque

### 3. Analyse CSV en Masse
1. Allez sur http://localhost:3000/bulk
2. Uploadez `sample_documents/sample_transactions.csv`
3. Voir le traitement de 100+ transactions
4. Voir la distribution des risques

### 4. Dashboard
1. Allez sur http://localhost:3000
2. Voir les statistiques en temps réel
3. Voir les analyses récentes
4. Accès rapide aux fonctionnalités

## 📁 Structure du Projet

```
VORTEX-AML/
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── pages/        # 8 pages complètes
│   │   ├── components/   # Layout + composants
│   │   └── services/     # API client
│   └── package.json
│
├── src/                   # Backend Python
│   ├── api.py            # FastAPI routes
│   ├── document_processor.py  # LandingAI integration
│   ├── screening_engine.py    # Risk analysis
│   ├── models.py         # Data models
│   └── aws_services.py   # AWS Bedrock
│
├── .env                   # Configuration
├── config.py             # Service mode logic
├── run.py                # Backend starter
└── start-all.bat         # Start everything
```

## 🛠️ Commandes Utiles

### Vérifier le Status
```bash
python check_services.py
```

### Tester les Services AI
```bash
python test_ai_integration.py
```

### Démarrer Backend Seul
```bash
python run.py
```

### Démarrer Frontend Seul
```bash
cd frontend
npm run dev
```

### Voir les Logs Backend
Le terminal backend affiche tous les logs en temps réel

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation principale |
| `SYSTEM_STATUS.md` | Status détaillé du système |
| `AI_SERVICES_SETUP.md` | Configuration AI complète |
| `ENABLE_BEDROCK.md` | Guide activation Bedrock |
| `frontend/README.md` | Documentation frontend |

## 🎯 Pour Votre Démo/Hackathon

### Ce Qui Impressionne
1. ✅ **Extraction AI réelle** (LandingAI)
2. ✅ **Interface professionnelle** (React)
3. ✅ **Analyse en temps réel** (<5 secondes)
4. ✅ **Bulk processing** (100+ transactions)
5. ✅ **Dashboard interactif**

### Points Forts à Montrer
- Upload d'un document → Extraction automatique
- Screening d'une entité → Résultats instantanés
- CSV bulk → Traitement de masse
- Dashboard → Statistiques en temps réel
- SAR generation → Conformité automatique

## 🔧 Besoin d'Aide?

### Problème: Frontend ne démarre pas
```bash
cd frontend
npm install
npm run dev
```

### Problème: Backend erreur
```bash
pip install -r requirements.txt
python run.py
```

### Problème: Port déjà utilisé
- Backend: Changez le port dans `run.py`
- Frontend: Changez le port dans `frontend/vite.config.js`

## 💡 Activer AWS Bedrock (Optionnel)

Si vous voulez activer le vrai LLM Bedrock:

1. Lisez `ENABLE_BEDROCK.md`
2. Obtenez des credentials AWS
3. Mettez à jour `.env`
4. Redémarrez: `start-all.bat`

**Mais ce n'est PAS nécessaire!** Votre config actuelle est excellente.

## 🎉 Prêt à Démarrer!

```bash
# Vérifiez que tout est OK
python check_services.py

# Démarrez l'application
start-all.bat

# Ouvrez votre navigateur
# http://localhost:3000
```

## 📞 Support

- **GitHub**: http://github.com/hosnibelfeki/VORTEX-AML
- **Email**: belfkihosni@gmail.com
- **LinkedIn**: https://www.linkedin.com/in/hosnibelfeki/

---

**Votre système VORTEX-AML est prêt! 🚀**

Modèle Bedrock configuré: ✅ `anthropic.claude-sonnet-4-5-20250929-v1:0`

Démarrez maintenant avec: `start-all.bat`
