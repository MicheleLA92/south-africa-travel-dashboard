# Kostenlos dauerhaft deployen

## Empfehlung: Streamlit Community Cloud

1. Projekt als GitHub-Repository hochladen.
2. Auf https://share.streamlit.io einloggen.
3. `New app` wählen.
4. Repository auswählen.
5. Main file path: `app.py`
6. Deploy klicken.

Danach bekommst du einen dauerhaften kostenlosen Link in dieser Form:

`https://DEIN-APP-NAME.streamlit.app`

## Alternative: Hugging Face Spaces

1. Auf https://huggingface.co/spaces einen neuen Space erstellen.
2. SDK: Streamlit wählen.
3. Dateien `app.py`, `requirements.txt` und Ordner `data/` hochladen.

Danach bekommst du einen kostenlosen Link in dieser Form:

`https://huggingface.co/spaces/DEIN-NAME/DEIN-SPACE`

## Telegram-Nachricht für Freunde-Quiz

Damit Michele bei jeder gespeicherten Freunde-Quiz-Antwort eine Telegram-Nachricht bekommt, in Streamlit Cloud unter App → Settings → Secrets eintragen:

```toml
[telegram]
bot_token = "123456:ABC..."
chat_id = "DEINE_CHAT_ID"
```

Ohne diese Secrets speichert die App Antworten weiterhin lokal in `data/friend_quiz_results.json`, versendet aber keine Nachricht.

## Passwort für privaten Upload-Ordner

Für den Upload-Ordner Michele & Roberto zusätzlich in Streamlit Cloud unter App → Settings → Secrets eintragen:

```toml
[upload]
password = "DEIN_PRIVATES_PASSWORT"
```

Hochgeladene Dateien werden im App-Ordner `uploads/` gespeichert und nicht nach GitHub gepusht.

## Hinweis

Cloudflare Quick Tunnel ist kostenlos, aber nicht dauerhaft. Für einen dauerhaft teilbaren Link brauchst du einen kostenlosen Hosting-Anbieter mit Account, z.B. Streamlit Community Cloud oder Hugging Face Spaces.
