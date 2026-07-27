import json
from collections import Counter
from pathlib import Path
from datetime import date, datetime

import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "sample_briefing.json"
QUIZ_RESULTS_PATH = ROOT / "data" / "friend_quiz_results.json"

st.set_page_config(
    page_title="Südafrika Reise",
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
.hero h1 { font-size: 2.5rem; margin: 0 0 1rem 0; letter-spacing: -0.04em; }
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
.quiz-score { font-size: 1.35rem; font-weight: 800; color: var(--green); margin: .2rem 0 .6rem 0; }
.quiz-answer { padding: .7rem .85rem; border-radius: 16px; margin: .4rem 0; background: rgba(234,216,183,.34); border: 1px solid rgba(49,92,69,.10); }
.quiz-answer strong { color: var(--green); }
.quiz-teaser {
  background: linear-gradient(120deg, rgba(255,250,241,.92), rgba(242,228,203,.94));
  border: 1px solid rgba(197,139,54,.26);
  border-radius: 24px;
  padding: 22px 24px;
  box-shadow: 0 16px 42px rgba(49,92,69,.09);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
}
.quiz-teaser h2 { margin: 0 0 .35rem 0; color: var(--green); letter-spacing: -.03em; }
.quiz-teaser p { margin: 0; color: var(--muted); max-width: 760px; }
.quiz-teaser .emoji { font-size: 2.2rem; margin-right: .35rem; }
@media (max-width: 760px) { .quiz-teaser { align-items:flex-start; flex-direction:column; } }
a { color: #8a5a16 !important; text-decoration: none; font-weight: 650; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data
def load_data():
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def select_daily_magic_place(data, current_date=None):
    """Pick one route-relevant Magic Place per day so the photo rotates."""
    current_date = current_date or date.today()
    places = data.get("magic_places") or [data["magic_place"]]
    return places[current_date.toordinal() % len(places)]


def load_quiz_results():
    if not QUIZ_RESULTS_PATH.exists():
        return []
    try:
        return json.loads(QUIZ_RESULTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_quiz_result(friend_name, quiz_questions, answers):
    QUIZ_RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    results = load_quiz_results()
    results.append(
        {
            "submitted_at": datetime.now().isoformat(timespec="seconds"),
            "name": friend_name,
            "answers": [
                {"question": question["question"], "answer": answer}
                for question, answer in zip(quiz_questions, answers)
            ],
        }
    )
    QUIZ_RESULTS_PATH.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return results


def summarize_quiz_results(results, quiz_questions):
    summary = []
    for question in quiz_questions:
        answers = [
            item["answer"]
            for result in results
            for item in result.get("answers", [])
            if item.get("question") == question["question"]
        ]
        counts = Counter(answers)
        top_answer, top_count = counts.most_common(1)[0] if counts else ("Noch keine Antwort", 0)
        summary.append(
            {
                "question": question["question"],
                "top_answer": top_answer,
                "top_count": top_count,
                "total": len(answers),
            }
        )
    return summary

data = load_data()
TRIP_START = date(2026, 8, 4)
days_until_trip = max((TRIP_START - date.today()).days, 0)

with st.sidebar:
    st.title("🌍 Südafrika")
    current_stop = st.selectbox("Etappe anzeigen", [s["name"] for s in data["route"]], index=0)
    st.divider()
    st.metric("Tage bis Abreise", days_until_trip)

st.markdown("""
<div class="hero">
  <span class="badge">Cape Town → East London → Johannesburg → Kruger</span>
  <h1>Südafrika Reise</h1>
</div>
""", unsafe_allow_html=True)

st.write("")

components.html(f"""
<style>
  .countdown-wrap {{
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0 0 2px 0;
    border-radius: 24px;
    padding: 18px 20px;
    background: rgba(255, 250, 241, .88);
    border: 1px solid rgba(49, 92, 69, .12);
    box-shadow: 0 14px 40px rgba(49,92,69,.08);
    color: #1f2a24;
  }}
  .countdown-head {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 12px;
  }}
  .countdown-title {{
    font-size: 1rem;
    font-weight: 800;
    color: #315c45;
    letter-spacing: .02em;
  }}
  .countdown-date {{ color: #6f766f; font-size: .9rem; }}
  .countdown-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
  .countdown-box {{
    border-radius: 18px;
    padding: 14px 10px;
    text-align: center;
    background: linear-gradient(180deg, #fffaf1, #f2e4cb);
    border: 1px solid rgba(49, 92, 69, .10);
  }}
  .countdown-box strong {{
    display: block;
    font-size: clamp(1.9rem, 5vw, 3.1rem);
    line-height: 1;
    letter-spacing: -.06em;
    font-variant-numeric: tabular-nums;
  }}
  .countdown-box span {{
    display: block;
    margin-top: 7px;
    color: #6f766f;
    font-size: .72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .12em;
  }}
  @media (max-width: 560px) {{ .countdown-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
</style>
<div class="countdown-wrap" role="timer" aria-live="polite">
  <div class="countdown-head">
    <div class="countdown-title">🇿🇦 Countdown bis zur Südafrika-Reise</div>
    <div class="countdown-date">Ziel: 4. August 2026 · noch {days_until_trip} Tage</div>
  </div>
  <div class="countdown-grid">
    <div class="countdown-box"><strong id="cd-days">—</strong><span>Tage</span></div>
    <div class="countdown-box"><strong id="cd-hours">—</strong><span>Stunden</span></div>
    <div class="countdown-box"><strong id="cd-minutes">—</strong><span>Minuten</span></div>
    <div class="countdown-box"><strong id="cd-seconds">—</strong><span>Sekunden</span></div>
  </div>
</div>
<script>
  const target = new Date('2026-08-04T00:00:00+02:00');
  const pad = value => String(value).padStart(2, '0');
  const el = id => document.getElementById(id);
  function tick() {{
    const now = new Date();
    const diff = target - now;
    if (diff <= 0) {{
      el('cd-days').textContent = '0';
      el('cd-hours').textContent = '00';
      el('cd-minutes').textContent = '00';
      el('cd-seconds').textContent = '00';
      return;
    }}
    const total = Math.floor(diff / 1000);
    el('cd-days').textContent = Math.floor(total / 86400);
    el('cd-hours').textContent = pad(Math.floor((total % 86400) / 3600));
    el('cd-minutes').textContent = pad(Math.floor((total % 3600) / 60));
    el('cd-seconds').textContent = pad(total % 60);
  }}
  tick();
  setInterval(tick, 1000);
</script>
""", height=178)

quiz = data.get("quiz", {})
quiz_questions = quiz.get("questions", []) if isinstance(quiz, dict) else quiz
if st.query_params.get("show") == "quiz":
    st.session_state["show_friend_quiz"] = True

st.write("")
st.markdown("""
<div class="quiz-teaser">
  <div>
    <h2><span class="emoji">🦁</span>Freunde-Quiz</h2>
    <p>Was glaubt ihr, was auf meiner Südafrika-Reise passieren wird?</p>
  </div>
</div>
""", unsafe_allow_html=True)

if st.button("Jetzt Vorhersage abgeben", type="primary", key="show_friend_quiz_button"):
    st.session_state["show_friend_quiz"] = True

if quiz_questions and st.session_state.get("show_friend_quiz", False):
    st.write("")
    st.markdown('<div id="freunde-quiz"></div>', unsafe_allow_html=True)
    st.subheader(f"🧠 {quiz.get('title', 'Südafrika-Quiz') if isinstance(quiz, dict) else 'Südafrika-Quiz'}")
    st.caption(
        quiz.get(
            "description",
            "Keine richtigen oder falschen Antworten – hier tippen deine Freunde, was unterwegs passiert.",
        )
        if isinstance(quiz, dict)
        else "Keine richtigen oder falschen Antworten – hier tippen deine Freunde, was unterwegs passiert."
    )

    friend_name = st.text_input("Dein Name", placeholder="z. B. Anna")
    answers = []
    answered_count = 0
    for index, question in enumerate(quiz_questions, start=1):
        options = ["– bitte wählen –", *question["options"]]
        answer = st.radio(
            f"{index}. {question['question']}",
            options,
            index=0,
            key=f"quiz_answer_{index}",
        )
        if answer != "– bitte wählen –":
            answered_count += 1
        answers.append(answer)

    st.progress(answered_count / len(quiz_questions), text=f"{answered_count} von {len(quiz_questions)} Tipps abgegeben")

    button_label = quiz.get("button_label", "Meine Tipps speichern") if isinstance(quiz, dict) else "Meine Tipps speichern"
    if st.button(button_label, type="primary", disabled=answered_count < len(quiz_questions) or st.session_state.get("quiz_checked", False)):
        display_name = friend_name.strip() or "Anonym"
        results = save_quiz_result(display_name, quiz_questions, answers)
        st.session_state["quiz_checked"] = True
        st.session_state["quiz_last_name"] = display_name
        st.session_state["quiz_last_answers"] = answers
        st.session_state["quiz_results"] = results

    if st.session_state.get("quiz_checked"):
        display_name = st.session_state.get("quiz_last_name", friend_name.strip() or "Anonym")
        submitted_answers = st.session_state.get("quiz_last_answers", answers)
        results = st.session_state.get("quiz_results", load_quiz_results())
        st.success("Danke! Deine Vorhersage wurde gespeichert.")
        st.markdown(
            f'<div class="card"><div class="quiz-score">{display_name}s Südafrika-Vorhersage</div>'
            '<div class="small">So hast du getippt:</div></div>',
            unsafe_allow_html=True,
        )
        for answer, question in zip(submitted_answers, quiz_questions):
            st.markdown(
                f'<div class="quiz-answer">🦁 <strong>{question["question"]}</strong><br>'
                f'<span class="small">Tipp: {answer}</span></div>',
                unsafe_allow_html=True,
            )

        st.subheader("📊 Auswertung bisher")
        for item in summarize_quiz_results(results, quiz_questions):
            st.markdown(
                f'<div class="quiz-answer">🏆 <strong>{item["question"]}</strong><br>'
                f'<span class="small">Meiste Antwort: {item["top_answer"]} '
                f'({item["top_count"]} von {item["total"]} Stimmen)</span></div>',
                unsafe_allow_html=True,
            )

st.write("")

left, right = st.columns([1.2, .8], gap="large")

with left:
    st.subheader("🗺️ Route & Etappen")

    map_route = data["map_route"]
    coastal_points = [point for point in map_route if point["kind"] == "coast"]
    inland_points = [point for point in map_route if point["kind"] != "coast"]
    route_points = [
        {
            **point,
            "position": [point["lon"], point["lat"]],
            "label": f"{index}. {point['name']}",
            "summary": "Küstenfahrt mit Mietwagen" if point["kind"] == "coast" else "Inland-Etappe Richtung Safari",
            "color": [20, 116, 139, 235] if point["kind"] == "coast" else [49, 92, 69, 235],
        }
        for index, point in enumerate(map_route, start=1)
    ]
    elephant_marker = {
        **data["map_elephant_marker"],
        "position": [data["map_elephant_marker"]["lon"], data["map_elephant_marker"]["lat"]],
        "summary": "Elefanten-Stop nahe Gqeberha / Port Elizabeth",
        "icon_data": {
            "url": data["map_elephant_marker"]["icon_url"],
            "width": 80,
            "height": 80,
            "anchorY": 80,
        },
    }
    coastal_path = [{"name": "Küstenroute Cape Town → East London", "path": [[point["lon"], point["lat"]] for point in coastal_points]}]
    inland_path = [{"name": "Inland & Safari East London → Johannesburg → Kruger", "path": [[point["lon"], point["lat"]] for point in [coastal_points[-1], *inland_points]]}]

    st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(latitude=-29.7, longitude=25.2, zoom=4.1, pitch=0),
            layers=[
                pdk.Layer(
                    "PathLayer",
                    coastal_path,
                    get_path="path",
                    get_color=[20, 116, 139, 245],
                    width_min_pixels=7,
                    rounded=True,
                    pickable=True,
                ),
                pdk.Layer(
                    "PathLayer",
                    inland_path,
                    get_path="path",
                    get_color=[197, 139, 54, 230],
                    width_min_pixels=5,
                    rounded=True,
                    pickable=True,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    route_points,
                    get_position="position",
                    get_fill_color="color",
                    get_line_color=[255, 250, 241, 255],
                    get_radius=22000,
                    line_width_min_pixels=2,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    route_points,
                    get_position="position",
                    get_text="label",
                    get_color=[31, 42, 36, 255],
                    get_size=14,
                    get_alignment_baseline="bottom",
                    get_pixel_offset=[0, -18],
                ),
                pdk.Layer(
                    "IconLayer",
                    [elephant_marker],
                    get_icon="icon_data",
                    get_position="position",
                    get_size=4,
                    size_scale=12,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    [elephant_marker],
                    get_position="position",
                    get_text="label",
                    get_color=[49, 92, 69, 255],
                    get_size=15,
                    get_alignment_baseline="top",
                    get_pixel_offset=[0, 26],
                ),
            ],
            tooltip={"html": "<b>{name}</b><br/>{summary}", "style": {"backgroundColor": "#315c45", "color": "#fffaf1"}},
        ),
        use_container_width=True,
        height=470,
    )
    st.caption("🐘 Kleiner Elefant = Addo Elephant National Park nahe Gqeberha / Port Elizabeth · Blau = Küstenfahrt Kapstadt bis East London · Gold = Inland-Etappe Richtung Johannesburg und Kruger.")

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


with right:
    st.subheader("✨ Magic Place des Tages")
    magic = select_daily_magic_place(data)
    st.image(magic["image"], caption=magic["caption"], use_container_width=True)
    st.markdown(f"### {magic['name']}")
    st.write(magic["description"])

st.write("")

c1, c2, c3 = st.columns(3)
with c1:
    st.subheader("📰 Aktuelle Lage")
    for item in data["briefing"]["news"]:
        st.write(f"• {item}")
with c2:
    st.subheader("🦟 Gesundheit")
    st.write(data["briefing"]["health"])
    st.progress(data["briefing"]["mosquito_level"] / 100, text=f"Mücken-/Malaria-Aufmerksamkeit: {data['briefing']['mosquito_level']}%")
with c3:
    st.subheader("🎒 Vorbereitung")
    for item in data["preparation"]:
        st.checkbox(item["task"], value=item["done"])

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
    </div>
    """, unsafe_allow_html=True)
    st.link_button("Restaurant öffnen", restaurant["link"])
with r2:
    st.markdown(f"""
    <div class="card">
      <h3>Unterkunft</h3>
      <h2>{stay['name']}</h2>
      <p>{stay['why']}</p>
    </div>
    """, unsafe_allow_html=True)
    st.link_button("Unterkunft öffnen", stay["link"])
