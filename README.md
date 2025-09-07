# 🔔 GitHub Release Monitor

Un bot Discord qui surveille automatiquement les nouvelles releases de vos repositories GitHub favoris et envoie des notifications.

## 🚀 Fonctionnalités

- ✅ Surveillance automatique de multiples repositories GitHub
- 🔔 Notifications Discord en temps réel
- 📊 API REST pour vérifications manuelles
- 🔄 Système de planification automatique (1 minute)
- 💾 Sauvegarde d'état pour éviter les doublons
- 🏥 Endpoints de santé pour monitoring

## 📋 Repositories surveillés par défaut

- **WildRig Multi** - andru-kun/wildrig-multi
- **OneZeroMiner** - OneZeroMiner/onezerominer  
- **SRBMiner Multi** - doktor83/SRBMiner-Multi
- **XMRig** - xmrig/xmrig
- **CPUMiner RPlant** - rplant8/cpuminer-opt-rplant
- **CPUMiner Opt** - jayddee/cpuminer-opt
- **Rigel** - rigelminer/rigel

## 🛠️ Installation et Configuration

### Prérequis
- Python 3.11+
- Compte GitHub avec token d'accès
- Serveur Discord avec webhook configuré

### 1. Clonage du projet
```bash
git clone https://github.com/Dasju64/github-release-monitor.git
cd github-release-monitor
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration des variables d'environnement
Copiez le fichier `.env.example` vers `.env` :
```bash
cp .env.example .env
```

Éditez le fichier `.env` avec vos propres valeurs :
```env
# Webhook Discord pour recevoir les notifications
DISCORD_WEBHOOK=https://discord.com/api/webhooks/VOTRE_WEBHOOK_ICI

# Token GitHub (personal access token avec scope "repo" ou "public_repo")
GITHUB_TOKEN=ghp_VOTRE_TOKEN_ICI

# Configuration Flask (pour déploiement)
FLASK_HOST=0.0.0.0
FLASK_PORT=10000
```

### 4. Obtenir un token GitHub
1. Allez dans **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**
2. Cliquez **"Generate new token (classic)"**
3. Donnez un nom à votre token
4. Sélectionnez le scope **"public_repo"** (ou "repo" pour les repos privés)
5. Cliquez **"Generate token"** et copiez-le

### 5. Créer un webhook Discord
1. Dans votre serveur Discord, allez dans **Paramètres du serveur** > **Intégrations**
2. Cliquez **"Créer un webhook"**
3. Choisissez le canal où recevoir les notifications
4. Copiez l'URL du webhook

## 🖥️ Utilisation

### Lancement local
```bash
python main.py
```

Le serveur démarre sur `http://localhost:5000`

### Endpoints disponibles
- **GET /** - Page d'accueil
- **GET /check** - Vérification manuelle des releases
- **GET /health** - Status de santé du service

### Exemple de vérification manuelle
```bash
curl http://localhost:5000/check
```

Réponse :
```json
{
  "status": "ok",
  "updated": true,
  "messages": [
    "🔢 Nouvelle release pour **xmrig**: https://github.com/xmrig/xmrig/releases/tag/v6.21.0"
  ]
}
```

## 🌐 Déploiement sur Render

### 1. Préparation
1. Poussez votre code sur GitHub
2. Créez un compte sur [render.com](https://render.com)

### 2. Création du service
1. Cliquez **"New"** > **"Web Service"**
2. Connectez votre repository GitHub
3. Configuration automatique via `render.yaml`

### 3. Variables d'environnement
Dans l'interface Render, ajoutez :
- `DISCORD_WEBHOOK` : votre webhook Discord
- `GITHUB_TOKEN` : votre token GitHub
- `FLASK_HOST` : `0.0.0.0`
- `FLASK_PORT` : `10000`

### 4. Déploiement
Cliquez **"Deploy"** - le service sera accessible via l'URL fournie par Render.

## ⚙️ Personnalisation

### Ajouter de nouveaux repositories
Éditez la variable `REPOS` dans `main.py` :
```python
REPOS = {
    "nom-affiché": "propriétaire/nom-repo",
    "mon-nouveau-repo": "user/repository",
}
```

### Modifier l'intervalle de vérification
Dans `main.py`, ligne du scheduler :
```python
scheduler.add_job(func=check_releases, trigger="interval", minutes=5)  # 5 minutes
```

### Personnaliser les messages Discord
Modifiez la variable `message` dans la fonction `check_releases()` :
```python
message = f"🆕 Nouveau: **{name}** - {release_url}"
```

## 📁 Structure du projet

```
github-release-monitor/
├── main.py              # Script principal
├── requirements.txt     # Dépendances Python
├── .env.example        # Exemple de configuration
├── .env               # Configuration (ignoré par git)
├── .gitignore         # Fichiers à ignorer
├── Procfile           # Configuration Heroku
├── render.yaml        # Configuration Render
├── state.json         # État des releases (généré automatiquement)
└── README.md          # Ce fichier
```

## 🐛 Dépannage

### Le bot ne trouve pas de nouvelles releases
- Vérifiez que votre token GitHub est valide
- Assurez-vous que les repositories existent et sont publics
- Consultez les logs pour les erreurs API

### Les messages ne s'envoient pas sur Discord
- Vérifiez l'URL du webhook Discord
- Testez le webhook manuellement avec curl
- Assurez-vous que le bot a les permissions dans le canal

### Erreurs de déploiement sur Render
- Vérifiez que toutes les variables d'environnement sont configurées
- Consultez les logs de déploiement dans l'interface Render
- Assurez-vous que le port est correctement configuré

## 📝 Logs et Monitoring

Le service inclut un système de logging détaillé. Pour voir les logs :

**En local :**
```bash
python main.py
```

**Sur Render :**
Consultez l'onglet "Logs" dans votre service.

## 🤝 Contribution

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/nouvelle-fonctionnalité`)
3. Committez vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalité`)
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Si vous rencontrez des problèmes :
1. Consultez la section [Dépannage](#-dépannage)
2. Vérifiez les [Issues GitHub](https://github.com/VOTRE_USERNAME/github-release-monitor/issues)
3. Créez une nouvelle issue si nécessaire

---


**⭐ N'hésitez pas à laisser une étoile si ce projet vous est utile !**

