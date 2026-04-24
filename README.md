# Grist AI Transformer Plugin (AI Transformer) 🤖

Ce plugin Grist permet d'automatiser le traitement de texte en utilisant une API **FastAPI** et un reverse-proxy **Caddy**. Très utile pour avoir une colonne de texte "Brut" et une colonne de texte retouché, anonymisé... pour des décideurs, une commission d'attribution d'aides...

- Le prompt est lu dans la table Grist `Config` (`Param`, `Value`) avec la clé `GRIST_AI_TRANSFORMER_PROMPT`.
- Le widget applique ce prompt aux lignes à traiter (`Source` → `Processed`).
- Les paramètres IA globaux restent dans `config/params.json` (`ai_api_url`, `ai_api_model`, `ai_api_key`, `temperature`).
