import requests
import json
import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Configuration Flask
app = Flask(__name__)

REPOS = {
    "wildrig-multi": "andru-kun/wildrig-multi",
    "onezerominer": "OneZeroMiner/onezerominer",
    "srbminer-multi": "doktor83/SRBMiner-Multi",
    "xmrig": "xmrig/xmrig",
    "cpuminer-rplant": "rplant8/cpuminer-opt-rplant",
    "cpuminer-opt": "jayddee/cpuminer-opt",
    "rigel": "rigelminer/rigel",
}

STATE_FILE = "state.json"
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL = "https://api.github.com/graphql"

# Vérification des variables d'environnement
if not WEBHOOK_URL or not GITHUB_TOKEN:
    logger.error("Variables d'environnement DISCORD_WEBHOOK et GITHUB_TOKEN requises")
    exit(1)

def load_state():
    try:
        if not os.path.exists(STATE_FILE):
            return {}
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de l'état: {e}")
        return {}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de l'état: {e}")

def build_graphql_query(repos):
    queries = []
    for i, (name, full_name) in enumerate(repos.items()):
        owner, repo = full_name.split("/")
        queries.append(f"""
        repo{i}: repository(owner: "{owner}", name: "{repo}") {{
            latestRelease: releases(first: 1, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
                nodes {{
                    id
                    name
                    tagName
                    url
                }}
            }}
        }}
        """)
    return "query { " + "\n".join(queries) + " }"

def get_latest_releases(repos):
    try:
        headers = {
            "Authorization": f"bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        query = build_graphql_query(repos)
        response = requests.post(GITHUB_API_URL, headers=headers, json={"query": query}, timeout=30)
        
        if response.status_code != 200:
            logger.error(f"Erreur API GraphQL: {response.status_code} - {response.text}")
            return None
        return response.json().get("data")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur réseau lors de la requête GitHub: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la requête GitHub: {e}")
        return None

def send_to_discord(message):
    try:
        data = {"content": message}
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code != 204:
            logger.error(f"Erreur envoi Discord: {response.status_code} - {response.text}")
        else:
            logger.info("Message envoyé avec succès à Discord")
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur réseau lors de l'envoi Discord: {e}")
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'envoi Discord: {e}")

def check_releases():
    try:
        logger.info("Vérification des nouvelles releases...")
        state = load_state()
        updated = False
        messages = []
        releases_data = get_latest_releases(REPOS)
        
        if not releases_data:
            return {"status": "error", "message": "Impossible de récupérer les releases."}
        
        for i, (name, _) in enumerate(REPOS.items()):
            repo_key = f"repo{i}"
            nodes = releases_data.get(repo_key, {}).get("latestRelease", {}).get("nodes", [])
            if not nodes:
                continue
            
            release = nodes[0]
            release_id = release["id"]
            release_url = release["url"]
            
            if state.get(name, {}).get("release_id") != release_id:
                message = f"📢 Nouvelle release pour **{name}**: {release_url}"
                logger.info(message)
                send_to_discord(message)
                state[name] = {"release_id": release_id}
                messages.append(message)
                updated = True
        
        if updated:
            save_state(state)
        
        logger.info(f"Vérification terminée. Mises à jour: {len(messages)}")
        return {"status": "ok", "updated": updated, "messages": messages}
    
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des releases: {e}")
        return {"status": "error", "message": str(e)}

# --- Routes Flask ---
@app.route("/")
def home():
    return "🚀 Serveur Flask opérationnel avec scheduler !"

@app.route("/check", methods=["GET"])
def check():
    result = check_releases()
    return jsonify(result)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "github-release-monitor"})

# --- Planification automatique ---
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_releases, trigger="interval", minutes=1)  # toutes les 1 minute
scheduler.start()

# Arrêt propre du scheduler
atexit.register(lambda: scheduler.shutdown())

# Configuration pour le déploiement sur Render
host = os.getenv("FLASK_HOST", "0.0.0.0")
port = int(os.getenv("FLASK_PORT", 5000))

if __name__ == "__main__":
    try:
        logger.info(f"Démarrage du serveur sur {host}:{port}")
        app.run(host=host, port=port, debug=False)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Arrêt du serveur...")

        scheduler.shutdown()
