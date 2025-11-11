# VORTEX-AML Frontend

Frontend React + Vite pour la plateforme VORTEX-AML (Anti-Money Laundering Intelligence System).

## 🚀 Démarrage Rapide

### Installation

```bash
cd frontend
npm install
```

### Développement

```bash
npm run dev
```

L'application sera disponible sur `http://localhost:3000`

### Build Production

```bash
npm run build
npm run preview
```

## 📁 Structure du Projet

```
frontend/
├── src/
│   ├── components/
│   │   └── Layout.jsx          # Layout principal avec sidebar
│   ├── pages/
│   │   ├── Dashboard.jsx       # Tableau de bord
│   │   ├── ManualScreening.jsx # Screening manuel
│   │   ├── DocumentUpload.jsx  # Upload de documents
│   │   ├── BulkAnalysis.jsx    # Analyse CSV en masse
│   │   ├── AnalysesList.jsx    # Liste des analyses
│   │   ├── AnalysisDetail.jsx  # Détails d'une analyse
│   │   ├── Cases.jsx           # Cas de conformité
│   │   └── Reports.jsx         # Rapports de conformité
│   ├── services/
│   │   └── api.js              # Service API
│   ├── App.jsx                 # Composant principal
│   ├── main.jsx                # Point d'entrée
│   └── index.css               # Styles globaux
├── index.html
├── vite.config.js
└── package.json
```

## 🎨 Fonctionnalités

### 1. Dashboard
- Statistiques en temps réel
- Analyses récentes
- Actions rapides
- Visualisation des risques

### 2. Screening Manuel
- Recherche d'entités par nom
- Évaluation des risques en temps réel
- Détails des flags et recommandations

### 3. Upload de Documents
- Drag & drop de fichiers
- Support multi-formats (PDF, Images, Word, CSV, Excel)
- Extraction automatique de données
- Évaluation des risques

### 4. Analyse en Masse (CSV)
- Upload de fichiers CSV
- Traitement de plusieurs transactions
- Distribution des risques
- Résultats détaillés

### 5. Liste des Analyses
- Filtrage par niveau de risque
- Pagination
- Recherche
- Export

### 6. Détails d'Analyse
- Vue complète d'une analyse
- Génération de SAR
- Historique complet
- Actions disponibles

### 7. Cas de Conformité
- Gestion des cas
- Assignation
- Suivi du statut
- Audit trail

### 8. Rapports
- Génération de rapports de conformité
- Export PDF/JSON
- Templates prédéfinis
- Statistiques réglementaires

## 🔌 API Backend

Le frontend communique avec le backend FastAPI sur `http://localhost:8000`

### Endpoints Utilisés

- `GET /health` - Health check
- `GET /dashboard/stats` - Statistiques du dashboard
- `POST /analyze/manual` - Screening manuel
- `POST /analyze/upload` - Upload de document
- `POST /analyze/csv` - Analyse CSV en masse
- `GET /analyses` - Liste des analyses
- `GET /analysis/:id` - Détails d'une analyse
- `POST /sars/generate` - Génération de SAR
- `GET /cases` - Cas de conformité
- `POST /reports/compliance` - Rapports de conformité

## 🎨 Design System

### Couleurs

```css
--primary: #2563eb (Bleu)
--secondary: #10b981 (Vert)
--danger: #ef4444 (Rouge)
--warning: #f59e0b (Orange)
--success: #10b981 (Vert)
```

### Niveaux de Risque

- **LOW** (0-19): Vert
- **MEDIUM** (20-49): Orange
- **HIGH** (50-74): Orange foncé
- **CRITICAL** (75-100): Rouge

## 🛠️ Technologies

- **React 18** - Framework UI
- **Vite** - Build tool
- **React Router** - Routing
- **Axios** - HTTP client
- **Lucide React** - Icônes
- **CSS3** - Styling

## 📝 Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine du dossier frontend:

```env
VITE_API_URL=http://localhost:8000
```

### Proxy API

Le fichier `vite.config.js` configure un proxy pour éviter les problèmes CORS en développement:

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, '')
    }
  }
}
```

## 🚀 Déploiement

### Build

```bash
npm run build
```

Les fichiers de production seront dans le dossier `dist/`

### Serveur de Production

```bash
npm run preview
```

Ou utilisez un serveur web comme Nginx, Apache, ou déployez sur:
- Vercel
- Netlify
- AWS S3 + CloudFront
- Azure Static Web Apps

## 📱 Responsive Design

L'application est entièrement responsive et fonctionne sur:
- Desktop (1920px+)
- Laptop (1366px+)
- Tablet (768px+)
- Mobile (320px+)

## 🔒 Sécurité

- Validation des entrées côté client
- Sanitization des données
- Protection CSRF via tokens
- HTTPS en production
- Gestion sécurisée des tokens

## 🤝 Contribution

1. Fork le projet
2. Créez une branche (`git checkout -b feature/amazing-feature`)
3. Commit vos changements (`git commit -m 'Add amazing feature'`)
4. Push vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📄 License

MIT License - voir le fichier LICENSE pour plus de détails

## 👨‍💻 Auteur

**Hosni Belfeki**
- LinkedIn: [hosnibelfeki](https://www.linkedin.com/in/hosnibelfeki/)
- Email: belfkihosni@gmail.com
- GitHub: [hosnibelfeki](https://github.com/hosnibelfeki)

---

© 2025 VORTEX-AML | Enterprise Anti-Money Laundering Platform
