import json
from pathlib import Path
from datetime import date

import streamlit as st

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "sample_briefing.json"

st.set_page_config(
    page_title="Südafrika Travel Bot Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --bg: #f6efe4;
  --panel: #fffaf1;
  --ink: #1f2a24;
  --muted: #6f766f;
  --green: #315c45;
  --gold: #c58b36;
  --sand: #ead8b7;
  --red: #a44a3f;
}
.stApp { background: linear-gradient(135deg, #f8f0df 0%, #eef3ea 55%, #f6efe4 100%); color: var(--ink); }
.block-container { padding-top: 1.6rem; padding-bottom: 2rem; }
.hero {
  border-radius: 28px;
  padding: 30px 34px;
  background: linear-gradient(120deg, rgba(49,92,69,.94), rgba(31,42,36,.9)),
              url('https://images.unsplash.com/photo-1484318571209-661cf29a69c3?q=80&w=1600&auto=format&fit=crop');
  background-size: cover;
  background-position: center;
  color: #fffaf1;
  box-shadow: 0 24px 70px rgba(31,42,36,.18);
}
.hero h1 { font-size: 2.5rem; margin: 0 0 .35rem 0; letter-spacing: -0.04em; }
.hero p { max-width: 780px; color: rgba(255,250,241,.86); font-size: 1.05rem; }
.badge { display:inline-block; padding:.35rem .7rem; border-radius:999px; background:rgba(255,250,241,.16); border:1px solid rgba(255,250,241,.24); margin-right:.4rem; font-size:.82rem; }
.card {
  background: rgba(255,250,241,.82);
  border: 1px solid rgba(49,92,69,.12);
  border-radius: 22px;
  padding: 20px 22px;
  box-shadow: 0 14px 40px rgba(49,92,69,.08);
  min-height: 145px;
}
.card h3 { margin-top: 0; color: var(--green); font-size: 1rem; text-transform: uppercase; letter-spacing: .08em; }
.metric { font-size: 2rem; font-weight: 760; letter-spacing: -.04em; color: var(--ink); }
.small { color: var(--muted); font-size: .9rem; }
.timeline { position: relative; padding-left: 12px; }
.stop {
  border-left: 4px solid var(--sand);
  padding: 0 0 18px 18px;
  margin: 0;
}
.stop.active { border-left-color: var(--gold); }
.stop h4 { margin: 0 0 4px 0; }
.pill { display:inline-block; margin:.2rem .25rem .2rem 0; padding:.25rem .55rem; border-radius:999px; background:#efe2c8; color:#315c45; font-size:.78rem; }
.risk-low { color:#2d6a4f; font-weight:700; }
.risk-medium { color:#b7791f; font-weight:700; }
.risk-high { color:#a44a3f; font-weight:700; }
a { color: #8a5a16 !important; text-decoration: none; font-weight: 650; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))

data = load_data()

with st.sidebar:
    st.title("🌍 Travel Bot")
    st.caption("Dashboard-Prototyp B: Streamlit")
    current_stop = st.selectbox("Etappe anzeigen", [s["name"] for s in data["route"]], index=0)
    show_archived = st.toggle("Archiv anzeigen", value=True)
    st.divider()
    st.metric("Tage bis August", data["trip"]["days_until_august"])
    st.caption("Später: Live-Daten aus Hermes Cronjob, JSON oder Telegram-Archiv.")

st.markdown(f"""
<div class="hero">
  <span class="badge">{data['briefing']['date']}</span>
  <span class="badge">Cape Town → Durban → Johannesburg → Kruger</span>
  <span class="badge">Daily Travel Briefing</span>
  <h1>Südafrika Reise-Dashboard</h1>
  <p>{data['briefing']['intro']}</p>
</div>
""", unsafe_allow_html=True)

st.write("")

m1, m2, m3, m4 = st.columns(4)
metrics = data["briefing"]["metrics"]
for col, item in zip([m1, m2, m3, m4], metrics):
    with col:
        st.markdown(f"""
        <div class="card">
          <h3>{item['label']}</h3>
          <div class="metric">{item['value']}</div>
          <div class="small">{item['hint']}</div>
        </div>
        """, unsafe_allow_html=True)

st.write("")
left, right = st.columns([1.2, .8], gap="large")

with left:
    st.subheader("🗺️ Route & Etappen")
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    for stop in data["route"]:
        active = "active" if stop["name"] == current_stop else ""
        tags = "".join(f'<span class="pill">{tag}</span>' for tag in stop["tags"])
        risk_class = f"risk-{stop['risk'].lower()}"
        st.markdown(f"""
        <div class="stop {active}">
          <h4>{stop['emoji']} {stop['name']}</h4>
          <div class="small">{stop['summary']}</div>
          <div>{tags}</div>
          <div class="small">Risiko/Planung: <span class="{risk_class}">{stop['risk_de']}</span> · Wetter: {stop['weather']}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    selected = next(s for s in data["route"] if s["name"] == current_stop)
    with st.expander(f"Details zu {current_stop}", expanded=True):
        st.write(selected["detail"])
        st.link_button("Info / Karte öffnen", selected["link"])

with right:
    st.subheader("✨ Magic Place des Tages")
    magic = data["magic_place"]
    st.image(magic["image"], caption=magic["caption"], use_container_width=True)
    st.markdown(f"### {magic['name']}")
    st.write(magic["description"])
    st.link_button("Mehr Infos", magic["link"])

st.write("")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📰 Aktuelle Lage")
    for item in data["briefing"]["news"]:
        st.write(f"• {item}")
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🦟 Gesundheit")
    st.write(data["briefing"]["health"])
    st.progress(data["briefing"]["mosquito_level"] / 100, text=f"Mücken-/Malaria-Aufmerksamkeit: {data['briefing']['mosquito_level']}%")
    st.markdown('</div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎒 Vorbereitung")
    for item in data["preparation"]:
        st.checkbox(item["task"], value=item["done"])
    st.markdown('</div>', unsafe_allow_html=True)

st.write("")
st.subheader("🍽️ Must-Visit & 🛏️ Must-Book")
r1, r2 = st.columns(2)
restaurant = data["restaurant"]
stay = data["stay"]
with r1:
    st.markdown(f"""
    <div class="card">
      <h3>Restaurant</h3>
      <h2>{restaurant['name']}</h2>
      <p>{restaurant['why']}</p>
      <p class="small">Ort: {restaurant['location']} · Hinweis: {restaurant['tip']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("Restaurant öffnen", restaurant["link"])
with r2:
    st.markdown(f"""
    <div class="card">
      <h3>Unterkunft</h3>
      <h2>{stay['name']}</h2>
      <p>{stay['why']}</p>
      <p class="small">Ort: {stay['location']} · Hinweis: {stay['tip']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("Unterkunft öffnen", stay["link"])

if show_archived:
    st.write("")
    st.subheader("📚 Briefing-Archiv")
    for entry in data["archive"]:
        with st.expander(entry["title"]):
            st.write(entry["text"])

st.caption("Prototyp: Daten kommen aktuell aus data/sample_briefing.json. Nächster Schritt: Live-Connector für Hermes Cronjob-Ausgaben oder Travel-Bot-JSON.")
