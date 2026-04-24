## 🏗 Architecture

1.  **Grist (Frontend)** : Un Custom Widget surveille la colonne `Source`.
2.  **Caddy (Proxy)** : Gère le HTTPS et redirige les requêtes vers l'API.
3.  **FastAPI (Backend)** : Reçoit le texte + le prompt transmis par le widget et interroge le LLM.
4.  **Llama (IA)** : Traite le texte et renvoie le résultat.
5.  **Grist (Update)** : Le widget écrit le résultat dans la colonne `Processed`.

## 🚀 Installation

### 1. Cloner le dépôt GitHub

```bash
git clone https://github.com/fredt34/grist-ai-transformer
cd grist-ai-transformer
```

### 2. Backend (FastAPI)
Installez les dépendances :

```bash
pip install fastapi uvicorn httpx python-multipart
```

Lancez le serveur :

```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```

### 3. Paramètres globaux (`config/params.json`)

Créez le fichier suivant (non versionné) :

```json
{
  "ai_api_url": "https://api.openai.com/v1/responses",
  "ai_api_model": "gpt-5.4",
  "ai_api_key": "sk-proj-...",
  "temperature": 0.2
}
```

### 4. Configuration du prompt dans Grist

Créez une table `Config` avec deux colonnes :

- `Param`
- `Value`

Ajoutez une ligne :

- `Param = GRIST_AI_TRANSFORMER_PROMPT`
- `Value = <votre prompt complet>`

Le prompt défini dans cette ligne est appliqué par le widget.

### 5. Proxy (Caddy)

Ajoutez ceci à votre Caddyfile pour lier le frontend et l'API :

```code
votre-plugin.entreprise.com {
    root * ./frontend
    file_server
    handle_path /api/* {
        reverse_proxy localhost:8000
    }
}
```

# ⚙️ Configuration Grist

## 1. Colonnes requises :

* `Source` (Texte ou Markdown)
* `Processed` (Texte ou Markdown)

Le prompt est lu dans la table `Config` (ligne `GRIST_AI_TRANSFORMER_PROMPT`).

## 2. Widget :

* Ajouter un widget **Custom**.
* URL : https://votre-plugin.entreprise.com/grist-plugin/index.html.
* Access Level : **Full Access**.
* Mappez les colonnes `Source` et `Processed` dans les options du widget.

# 🛠 Développement

- `main.py` : Contient la logique FastAPI et l'appel httpx vers l'API Llama.
- `grist-plugin/index.html` : Utilise grist-plugin-api.js, lit le prompt dans la table `Config` et l'applique aux lignes à traiter (onRecord).

# 🔒 Sécurité

Les clés API et URLs internes sont masquées derrière le backend.

Utilisez le filtrage IP ou le forward_auth de Caddy pour restreindre l'accès au plugin.