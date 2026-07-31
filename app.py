import base64
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from datetime import date, datetime

import pydeck as pdk
import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "sample_briefing.json"
QUIZ_RESULTS_PATH = ROOT / "data" / "friend_quiz_results.json"
UPLOAD_DIR = ROOT / "uploads"

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
/* iOS/Safari can inherit white text for Streamlit radio labels; force quiz widgets back to dark readable text. */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[role="radiogroup"] label,
div[role="radiogroup"] label p,
div[role="radiogroup"] label span,
div[data-testid="stWidgetLabel"] p {
  color: var(--ink) !important;
  opacity: 1 !important;
  text-shadow: none !important;
}
@media (max-width: 760px) {
  .quiz-teaser { align-items:flex-start; flex-direction:column; }
  div[data-testid="stRadio"] label p { font-size: 1rem !important; line-height: 1.35 !important; }
}
a { color: #8a5a16 !important; text-decoration: none; font-weight: 650; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

components.html("""
<script>
(function () {
  const parentWindow = window.parent;
  const parentDoc = parentWindow.document;
  const isMobile = () => parentWindow.innerWidth <= 760;
  const introKey = "south_africa_sidebar_intro_collapsed_v2";
  const listenerKey = "south_africa_sidebar_link_listener_v2";

  function openSidebar() {
    const expandButton = parentDoc.querySelector('button[data-testid="stExpandSidebarButton"]');
    if (expandButton) {
      expandButton.click();
      return true;
    }
    return false;
  }

  function closeSidebar() {
    const sidebar = parentDoc.querySelector('section[data-testid="stSidebar"]');
    if (!sidebar) return false;

    const closeButton =
      sidebar.querySelector('button[aria-label="Close sidebar"]') ||
      sidebar.querySelector('button[title="Close sidebar"]') ||
      sidebar.querySelector('button[data-testid="stSidebarCollapseButton"]') ||
      sidebar.querySelector('button[data-testid="stBaseButton-headerNoPadding"]') ||
      sidebar.querySelector('button[kind="headerNoPadding"]') ||
      sidebar.querySelector('button[kind="header"]');

    if (closeButton) {
      closeButton.click();
      return true;
    }
    return false;
  }

  if (!parentWindow[listenerKey]) {
    parentWindow[listenerKey] = true;
    parentDoc.addEventListener("click", function (event) {
      const link = event.target.closest('section[data-testid="stSidebar"] a');
      if (!link || !isMobile()) return;
      setTimeout(function () {
        if (closeSidebar()) return;
        setTimeout(closeSidebar, 350);
      }, 180);
    }, true);
  }

  if (isMobile() && parentWindow.sessionStorage.getItem(introKey) !== "1") {
    parentWindow.sessionStorage.setItem(introKey, "1");
    setTimeout(openSidebar, 250);
    setTimeout(function () {
      if (closeSidebar()) return;
      setTimeout(closeSidebar, 900);
    }, 3800);
  }
})();
</script>
""", height=0)

def load_data():
    # Keep JSON edits immediately visible on Streamlit Cloud; route/content changes
    # are tiny, so caching this file is not worth stale dashboard data.
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def image_source_for_gallery(image_path):
    if image_path.startswith(("http://", "https://")):
        return image_path
    local_path = ROOT / image_path
    suffix = local_path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/webp" if suffix == ".webp" else "image/jpeg"
    encoded = base64.b64encode(local_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def render_image_carousel(image_paths, carousel_id):
    image_sources = [image_source_for_gallery(path) for path in image_paths]
    if not image_sources:
        return
    components.html(f"""
<div id="{carousel_id}" class="stay-carousel">
  <img class="stay-carousel-image" alt="Unterkunft Marloth Park" />
  <button class="stay-carousel-arrow stay-carousel-prev" type="button" aria-label="Vorheriges Bild">‹</button>
  <button class="stay-carousel-arrow stay-carousel-next" type="button" aria-label="Nächstes Bild">›</button>
  <div class="stay-carousel-count"></div>
</div>
<script>
(function() {{
  const images = {json.dumps(image_sources)};
  const root = document.getElementById({json.dumps(carousel_id)});
  const img = root.querySelector('.stay-carousel-image');
  const count = root.querySelector('.stay-carousel-count');
  let index = 0;
  function show(nextIndex) {{
    index = (nextIndex + images.length) % images.length;
    img.src = images[index];
    count.textContent = `Bild ${{index + 1}} von ${{images.length}}`;
  }}
  root.querySelector('.stay-carousel-prev').addEventListener('click', function() {{ show(index - 1); }});
  root.querySelector('.stay-carousel-next').addEventListener('click', function() {{ show(index + 1); }});
  show(0);
  if (images.length > 1) {{
    setInterval(function() {{ show(index + 1); }}, 2000);
  }}
}})();
</script>
<style>
  .stay-carousel {{
    position: relative;
    width: 100%;
    height: 300px;
    border-radius: 20px;
    overflow: hidden;
    background: #ead8b7;
    box-shadow: 0 12px 30px rgba(31, 42, 36, .16);
    margin-bottom: 0.8rem;
  }}
  .stay-carousel-image {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}
  .stay-carousel-arrow {{
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 42px;
    height: 42px;
    border-radius: 999px;
    border: 0;
    background: rgba(31, 42, 36, .58);
    color: white;
    font-size: 34px;
    line-height: 36px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding-bottom: 4px;
  }}
  .stay-carousel-prev {{ left: 12px; }}
  .stay-carousel-next {{ right: 12px; }}
  .stay-carousel-count {{
    position: absolute;
    left: 50%;
    bottom: 10px;
    transform: translateX(-50%);
    background: rgba(31, 42, 36, .62);
    color: #fffaf1;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 12px;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }}
  @media (max-width: 760px) {{
    .stay-carousel {{ height: 230px; border-radius: 16px; }}
    .stay-carousel-arrow {{ width: 36px; height: 36px; font-size: 30px; }}
  }}
</style>
""", height=325)


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


def build_quiz_notification_message(friend_name, quiz_questions, answers):
    lines = ["🦁 Neue Freunde-Quiz Antwort", f"Name: {friend_name}", ""]
    for index, (question, answer) in enumerate(zip(quiz_questions, answers), start=1):
        lines.append(f"{index}. {question['question']}")
        lines.append(f"Antwort: {answer}")
        lines.append("")
    return "\n".join(lines).strip()


def get_telegram_notification_config():
    try:
        telegram = st.secrets.get("telegram", {})
        token = telegram.get("bot_token") or st.secrets.get("TELEGRAM_BOT_TOKEN")
        chat_id = telegram.get("chat_id") or st.secrets.get("TELEGRAM_CHAT_ID")
    except Exception:
        return None, None
    return token, chat_id


def notify_quiz_submission(friend_name, quiz_questions, answers):
    token, chat_id = get_telegram_notification_config()
    if not token or not chat_id:
        return "not_configured"

    message = build_quiz_notification_message(friend_name, quiz_questions, answers)
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": message}).encode("utf-8")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        with urllib.request.urlopen(url, data=payload, timeout=8) as response:
            return "sent" if response.status == 200 else "failed"
    except Exception:
        return "failed"


def get_upload_password():
    try:
        upload = st.secrets.get("upload", {})
        return upload.get("password") or st.secrets.get("UPLOAD_PASSWORD")
    except Exception:
        return None


def safe_upload_filename(filename):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", filename or "upload")
    return cleaned.strip("._") or "upload"


def save_uploaded_file(uploaded_file):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = safe_upload_filename(uploaded_file.name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = UPLOAD_DIR / f"{timestamp}_{safe_name}"
    destination.write_bytes(uploaded_file.getbuffer())
    return destination


def render_quiz_answer_summary(quiz_questions):
    quiz_results = load_quiz_results()
    if quiz_results and quiz_questions:
        for item in summarize_quiz_results(quiz_results, quiz_questions):
            st.markdown(f"**{item['question']}**")
            for answer in item["answers"]:
                st.markdown(f"• {answer}")
    else:
        st.caption("Noch keine Antworten gespeichert.")


def render_private_upload_folder():
    upload_password = get_upload_password()
    if not upload_password:
        st.info('Upload ist vorbereitet. Bitte in Streamlit Secrets noch ein Passwort setzen: [upload] password = "..."')
    else:
        password = st.text_input("Passwort", type="password", key="private_upload_password")
        if password == upload_password:
            st.success("Upload Ordner entsperrt.")
            uploaded_files = st.file_uploader(
                "Bilder auswählen",
                type=["jpg", "jpeg", "png", "webp", "heic", "heif"],
                accept_multiple_files=True,
                key="private_photo_uploads",
            )
            if st.button("In Upload Ordner speichern", disabled=not uploaded_files, key="save_private_uploads"):
                saved_paths = [save_uploaded_file(file) for file in uploaded_files]
                st.success(f"{len(saved_paths)} Bild(er) im Upload Ordner gespeichert.")
                for path in saved_paths:
                    st.write(f"• uploads/{path.name}")
        elif password:
            st.error("Passwort stimmt nicht.")


def route_stop_anchor(stop_name):
    return "route-" + re.sub(r"[^a-z0-9]+", "-", stop_name.lower()).strip("-")


def render_route_stop(stop):
    st.markdown(f"**{stop['emoji']} {stop['name']}**")
    st.caption(stop["summary"])


def render_top_recommendation(data, category):
    restaurant = data.get("restaurant", {})
    stay = data.get("stay", {})
    activities = data.get("activities", [])

    if category == "Restaurant":
        if restaurant:
            st.markdown(f"**[{restaurant['name']}]({restaurant['link']})**")
            st.caption(restaurant["why"])
        else:
            st.caption("Noch kein Restaurant hinterlegt.")
    elif category == "Unterkunft":
        if stay:
            st.markdown(f"**[{stay['name']}]({stay['link']})**")
            st.caption(stay["why"])
        else:
            st.caption("Noch keine Unterkunft hinterlegt.")
    else:
        if activities:
            for activity in activities:
                st.markdown(f"• [{activity['name']}]({activity['link']})")
                if activity.get("why"):
                    st.caption(activity["why"])
        else:
            st.caption("Noch keine Aktivitäten hinterlegt.")


def summarize_quiz_results(results, quiz_questions):
    summary = []
    for question in quiz_questions:
        answers = [
            item["answer"]
            for result in results
            for item in result.get("answers", [])
            if item.get("question") == question["question"]
        ]
        unique_answers = list(dict.fromkeys(answers))
        summary.append(
            {
                "question": question["question"],
                "answers": unique_answers or ["Noch keine Antwort"],
            }
        )
    return summary

data = load_data()
TRIP_START = date(2026, 8, 4)
days_until_trip = max((TRIP_START - date.today()).days, 0)
quiz = data.get("quiz", {})
quiz_questions = quiz.get("questions", []) if isinstance(quiz, dict) else quiz

with st.sidebar:
    st.title("🌍 Südafrika")
    st.markdown("### Menü")
    with st.expander("🦁 Freunde-Quiz", expanded=False):
        st.markdown("[Quiz ansehen](#freunde-quiz)")
        st.markdown("[Bisherige Antworten](?show=answers#bisherige-antworten)")
    with st.expander("🗺️ Route & Etappen", expanded=False):
        st.markdown("[Route ansehen](#route-etappen)")
        for stop in data["route"]:
            st.markdown(f"[{stop['emoji']} {stop['name']}](#{route_stop_anchor(stop['name'])})")
    with st.expander("⭐ Top Empfehlungen", expanded=False):
        st.markdown("[Restaurant](#top-restaurant)")
        st.markdown("[Unterkunft](#top-unterkunft)")
        st.markdown("[Aktivitäten](#top-aktivitaeten)")
    st.divider()
    with st.expander("🔒 Privater Ordner", expanded=False):
        render_private_upload_folder()

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
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .countdown-flag {{ width: 1.35em; height: 1.35em; display: inline-block; }}
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
    <div class="countdown-title"><img class="countdown-flag" src="https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f1ff-1f1e6.png" alt="Südafrika-Flagge"> Countdown bis zur Südafrika-Reise</div>
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

show_quiz_answers = st.query_params.get("show") == "answers"

if st.query_params.get("show") == "quiz":
    st.session_state["show_friend_quiz"] = True

st.write("")
st.markdown('<div id="freunde-quiz"></div>', unsafe_allow_html=True)
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

if show_quiz_answers:
    st.markdown('<div id="bisherige-antworten"></div>', unsafe_allow_html=True)
    with st.expander("➜ Bisherige Antworten", expanded=True):
        render_quiz_answer_summary(quiz_questions)

if quiz_questions and st.session_state.get("show_friend_quiz", False):
    st.write("")
    st.subheader(f"🧠 {quiz.get('title', 'Südafrika-Quiz') if isinstance(quiz, dict) else 'Südafrika-Quiz'}")
    st.caption(
        quiz.get(
            "description",
            "Keine richtigen oder falschen Antworten – hier tippen deine Freunde, was unterwegs passiert.",
        )
        if isinstance(quiz, dict)
        else "Keine richtigen oder falschen Antworten – hier tippen deine Freunde, was unterwegs passiert."
    )

    st.markdown("**Dein Name**")
    friend_name = st.text_input("Dein Name", placeholder="z. B. Anna", label_visibility="collapsed")
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
        notification_status = notify_quiz_submission(display_name, quiz_questions, answers)
        st.session_state["quiz_checked"] = True
        st.session_state["quiz_last_name"] = display_name
        st.session_state["quiz_last_answers"] = answers
        st.session_state["quiz_results"] = results
        st.session_state["quiz_notification_status"] = notification_status

    if st.session_state.get("quiz_checked"):
        display_name = st.session_state.get("quiz_last_name", friend_name.strip() or "Anonym")
        submitted_answers = st.session_state.get("quiz_last_answers", answers)
        results = st.session_state.get("quiz_results", load_quiz_results())
        st.success("Danke! Deine Vorhersage wurde gespeichert.")
        st.markdown(
            f'<div class="card"><div class="quiz-score">{display_name}s Südafrika-Vorhersage</div>'
            '<div class="small">Deine Tipps und die bisher gewählten Antworten findest du unten.</div></div>',
            unsafe_allow_html=True,
        )

        result_view = st.selectbox(
            "Quiz Ergebnis anzeigen",
            ["Deine Antworten", "Bisher gewählte Antworten"],
            key="quiz_result_view",
        )
        if result_view == "Deine Antworten":
            for answer, question in zip(submitted_answers, quiz_questions):
                st.markdown(
                    f'<div class="quiz-answer">🦁 <strong>{question["question"]}</strong><br>'
                    f'<span class="small">Tipp: {answer}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            for item in summarize_quiz_results(results, quiz_questions):
                answer_lines = "<br>".join(f"• {answer}" for answer in item["answers"])
                st.markdown(
                    f'<div class="quiz-answer">📝 <strong>{item["question"]}</strong><br>'
                    f'<span class="small">{answer_lines}</span></div>',
                    unsafe_allow_html=True,
                )

st.write("")

left, right = st.columns([1.2, .8], gap="large")

with left:
    st.markdown('<div id="route-etappen"></div>', unsafe_allow_html=True)
    st.subheader("🗺️ Route & Etappen")

    map_route = data["map_route"]
    coastal_points = [point for point in map_route if point["kind"] == "coast"]
    inland_points = [point for point in map_route if point["kind"] != "coast"]
    route_points = [
        {
            **point,
            "position": [point["lon"], point["lat"]],
            "label": f"{index}. {point['name']}",
            "color": [20, 116, 139, 235] if point["kind"] == "coast" else [49, 92, 69, 235],
        }
        for index, point in enumerate(map_route, start=1)
    ]
    elephant_marker = {
        **data["map_elephant_marker"],
        "position": [data["map_elephant_marker"]["lon"], data["map_elephant_marker"]["lat"]],
        "label_text": "Addo Elephant Park",
        "icon_data": {
            "url": "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f418.png",
            "width": 72,
            "height": 72,
            "anchorY": 36,
        },
    }
    coastal_path = [{"name": "Küstenroute Cape Town → East London", "path": [[point["lon"], point["lat"]] for point in coastal_points]}]
    inland_path = [{"name": "✈️ Inland & Safari East London → Johannesburg → Kruger", "path": [[point["lon"], point["lat"]] for point in [coastal_points[-1], *inland_points]]}]

    st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(latitude=-29.2, longitude=25.2, zoom=3.75, pitch=0),
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
                    "ScatterplotLayer",
                    [elephant_marker],
                    get_position="position",
                    get_fill_color=[255, 193, 7, 250],
                    get_line_color=[31, 42, 36, 255],
                    get_radius=16000,
                    line_width_min_pixels=2,
                    pickable=True,
                ),
                pdk.Layer(
                    "IconLayer",
                    [elephant_marker],
                    get_icon="icon_data",
                    get_position="position",
                    get_size=1.5,
                    size_scale=12,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    [elephant_marker],
                    get_position="position",
                    get_text="label_text",
                    get_color=[49, 92, 69, 255],
                    get_size=11,
                    get_alignment_baseline="bottom",
                    get_pixel_offset=[0, -18],
                ),
            ],
            tooltip={"html": "<b>{name}</b>", "style": {"backgroundColor": "#315c45", "color": "#fffaf1"}},
        ),
        use_container_width=True,
        height=470,
    )
    st.caption("🐘 Kleiner Elefant = Addo Elephant National Park nahe Gqeberha / Port Elizabeth · Blau = Küstenfahrt Kapstadt bis East London · Gold = ✈️ Flug-/Inland-Etappe Richtung Johannesburg und Kruger.")

    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    for stop in data["route"]:
        tags = "".join(f'<span class="pill">{tag}</span>' for tag in stop["tags"])
        st.markdown(f"""
        <div id="{route_stop_anchor(stop['name'])}" class="stop">
          <h4>{stop['emoji']} {stop['name']}</h4>
          <div class="small">{stop['summary']}</div>
          <div>{tags}</div>
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
st.markdown('<div id="top-empfehlungen"></div>', unsafe_allow_html=True)
st.subheader("⭐ Top Empfehlungen")
r1, r2, r3 = st.columns(3)
restaurant = data["restaurant"]
restaurants = data.get("restaurants") or [restaurant]
stay = data["stay"]
stays = data.get("stays") or [stay]
activities = data.get("activities", [])
with r1:
    st.markdown('<div id="top-restaurant"></div>', unsafe_allow_html=True)
    for index, restaurant_item in enumerate(restaurants):
        tip_html = f"<p class=\"small\">{restaurant_item['tip']}</p>" if restaurant_item.get("tip") else ""
        st.markdown(f"""
        <div class="card">
          <h3>Restaurant · {restaurant_item.get('location', '')}</h3>
          <h2>{restaurant_item['name']}</h2>
          <p>{restaurant_item['why']}</p>
          {tip_html}
        </div>
        """, unsafe_allow_html=True)
        if restaurant_item.get("link"):
            st.link_button("Restaurant öffnen", restaurant_item["link"], key=f"restaurant_link_{index}")
with r2:
    st.markdown('<div id="top-unterkunft"></div>', unsafe_allow_html=True)
    for index, stay_item in enumerate(stays):
        gallery_images = stay_item.get("images") or ([stay_item["image"]] if stay_item.get("image") else [])
        if gallery_images:
            render_image_carousel(gallery_images, f"stay-carousel-{index}")
        tip_html = f"<p class=\"small\">{stay_item['tip']}</p>" if stay_item.get("tip") else ""
        st.markdown(f"""
        <div class="card">
          <h3>Unterkunft · {stay_item.get('location', '')}</h3>
          <h2>{stay_item['name']}</h2>
          <p>{stay_item['why']}</p>
          {tip_html}
        </div>
        """, unsafe_allow_html=True)
        if stay_item.get("link"):
            st.link_button("Unterkunft öffnen", stay_item["link"], key=f"stay_link_{index}")
with r3:
    st.markdown('<div id="top-aktivitaeten"></div>', unsafe_allow_html=True)
    if activities:
        activity = activities[0]
        st.markdown(f"""
        <div class="card">
          <h3>Aktivitäten</h3>
          <h2>{activity['name']}</h2>
          <p>{activity.get('why', 'Ausgewählte Aktivität für die Reise.')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("Aktivität öffnen", activity["link"])
    else:
        st.markdown("""
        <div class="card">
          <h3>Aktivitäten</h3>
          <h2>Noch offen</h2>
          <p>Hier ergänzen wir schöne Ausflüge, Aussichtspunkte und besondere Stopps.</p>
        </div>
        """, unsafe_allow_html=True)

