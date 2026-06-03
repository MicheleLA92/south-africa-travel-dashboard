# Südafrika Travel Bot Dashboard

Streamlit-Prototyp für Micheles Travel Bot.

## Starten

```bash
cd /home/michele/travel-dashboard
uv run --with streamlit streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Dann im Browser öffnen:

http://127.0.0.1:8501

## Datenquelle

Aktuell nutzt die App Demo-Daten aus:

`data/sample_briefing.json`

Der nächste sinnvolle Schritt ist ein Connector, der die echte Travel-Bot-Ausgabe in dieses JSON-Format schreibt, z.B.:

- Hermes Cronjob `Daily Travel Africa Update`
- Telegram-Archiv
- Markdown/Text-Briefings
- eine kleine SQLite-Datenbank

## Struktur

- `app.py` — Streamlit Dashboard
- `data/sample_briefing.json` — Demo-Datenmodell
- `README.md` — Start und nächste Schritte

## Richtung Option C

Wenn das visuelle Konzept passt, kann daraus später eine Next.js/React-App werden mit:

- interaktiver Karte
- persistentem Archiv
- Login/Share-Link
- schöneren Cards und Animationen
- Live-Quellen für Wetter, News und Reisehinweise
