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


def render_image_carousel(image_paths, carousel_id, autoplay_ms=2000, object_fit="cover", height_px=300):
    image_sources = [image_source_for_gallery(path) for path in image_paths]
    if not image_sources:
        return
    mobile_height_px = 320 if object_fit == "contain" else 230
    background = "linear-gradient(180deg, #fffaf1, #ead8b7)" if object_fit == "contain" else "#ead8b7"
    component_height = height_px + 25
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
  const autoplayMs = {int(autoplay_ms) if autoplay_ms else 0};
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
  if (images.length > 1 && autoplayMs > 0) {{
    setInterval(function() {{ show(index + 1); }}, autoplayMs);
  }}
}})();
</script>
<style>
  .stay-carousel {{
    position: relative;
    width: 100%;
    height: {height_px}px;
    border-radius: 20px;
    overflow: hidden;
    background: {background};
    box-shadow: 0 12px 30px rgba(31, 42, 36, .16);
    margin-bottom: 0.8rem;
  }}
  .stay-carousel-image {{
    width: 100%;
    height: 100%;
    object-fit: {object_fit};
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
    .stay-carousel {{ height: {mobile_height_px}px; border-radius: 16px; }}
    .stay-carousel-arrow {{ width: 36px; height: 36px; font-size: 30px; }}
  }}
</style>
""", height=component_height)


def select_daily_magic_place(data, current_date=None):
    """Pick one route-relevant Magic Place per day so the photo rotates."""
    current_date = current_date or date.today()
    places = data.get("magic_places") or [data["magic_place"]]
    override_name = data.get("magic_place_overrides", {}).get(current_date.isoformat())
    if override_name:
        override_place = next((place for place in places if place.get("name") == override_name), None)
        if override_place:
            return override_place
    return places[current_date.toordinal() % len(places)]


def load_quiz_results():
    if not QUIZ_RESULTS_PATH.exists():
        return []
    try:
        return json.loads(QUIZ_RESULTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def load_restored_quiz_results():
    try:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    restored = data.get("restored_quiz_results", [])
    return restored if isinstance(restored, list) else []


def get_all_quiz_results():
    merged = []
    seen = set()
    for result in [*load_restored_quiz_results(), *load_quiz_results()]:
        key = json.dumps(
            {
                "name": result.get("name"),
                "answers": result.get("answers", []),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if key in seen:
            continue
        seen.add(key)
        merged.append(result)
    return merged


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
    quiz_results = get_all_quiz_results()
    if quiz_results and quiz_questions:
        for item in summarize_quiz_results(quiz_results, quiz_questions):
            st.markdown(f"**{item['question']}**")
            for answer in item["answers"]:
                st.markdown(f"• {answer}")
    else:
        st.caption("Noch keine Antworten gespeichert.")


PHOTO_MAP_ICON_URL = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4f7.png"
RESTAURANT_MAP_ICON_URL = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f374.png"
ACTIVITY_MAP_ICON_URL = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f377.png"
ELEPHANT_MAP_ICON_URL = "https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f418.png"


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


def recommendation_images(item):
    return item.get("images") or ([item["image"]] if item.get("image") else [])


def photo_stop_icon_url(stop):
    if stop.get("kind") == "restaurant":
        return RESTAURANT_MAP_ICON_URL
    if stop.get("kind") == "activity":
        return ACTIVITY_MAP_ICON_URL
    return PHOTO_MAP_ICON_URL


def photo_stop_menu_icon(stop):
    if stop.get("kind") == "restaurant":
        return "🍴"
    if stop.get("kind") == "activity":
        return "🍷"
    return "📷"


def get_photo_stop_entries(data):
    photo_stops = [stop for stop in data.get("photo_stops", []) if stop.get("photos")]
    existing_names = {stop["name"] for stop in photo_stops}

    recommendation_sources = [
        ("restaurant", data.get("restaurants") or ([data.get("restaurant")] if data.get("restaurant") else [])),
        ("stay", data.get("stays") or ([data.get("stay")] if data.get("stay") else [])),
        ("activity", data.get("activities", [])),
    ]
    for recommendation_kind, items in recommendation_sources:
        for item in items:
            if not isinstance(item, dict) or item.get("name") in existing_names:
                continue
            images = recommendation_images(item)
            if not images or "lat" not in item or "lon" not in item:
                continue
            kind = "restaurant" if recommendation_kind == "restaurant" else ("activity" if recommendation_kind == "activity" else "photo")
            photo_stops.append(
                {
                    "name": item["name"],
                    "location": item.get("location", item["name"]),
                    "lat": item["lat"],
                    "lon": item["lon"],
                    "summary": item.get("why") or item.get("summary") or "Empfehlung mit Reisefotos.",
                    "region": item.get("region", "Weitere Spots"),
                    "kind": kind,
                    "photos": images,
                    "source": "top_recommendation",
                }
            )
            existing_names.add(item["name"])
    return photo_stops


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
            gallery_images = restaurant.get("images") or ([restaurant["image"]] if restaurant.get("image") else [])
            if gallery_images:
                render_image_carousel(gallery_images, "top-restaurant-carousel", autoplay_ms=3500, object_fit="contain", height_px=360)
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


def normalize_quiz_answer_text(answer):
    replacements = {
        "ich nenne es „Abenteuer“": "wir nennen es „Abenteuer“",
        "„Ich habe mich in das Frühstück verliebt.“": "„Wir haben uns in das Frühstück verliebt.“",
        "„Ich wollte nur Ferien machen, jetzt suche ich Wohnungen.“": "„Wir wollten nur Ferien machen, jetzt suchen wir Wohnungen.“",
        "„Das ist mein neues Lieblingsland.“": "„Das ist unser neues Lieblingsland.“",
        "„Ich brauche keinen Rückflug, ich brauche einen grösseren Koffer für den Elefanten.“": "„Wir brauchen keinen Rückflug, wir brauchen einen grösseren Koffer für den Elefanten.“",
    }
    return replacements.get(answer, answer)


def summarize_quiz_results(results, quiz_questions):
    summary = []
    for question_index, question in enumerate(quiz_questions):
        answers = []
        for result in results:
            result_answers = result.get("answers", [])
            for item_index, item in enumerate(result_answers):
                same_question = item.get("question") == question["question"]
                same_position = item_index == question_index
                if same_question or same_position:
                    answers.append(normalize_quiz_answer_text(item.get("answer", "")))
                    break
        unique_answers = list(dict.fromkeys(answer for answer in answers if answer))
        summary.append(
            {
                "question": question["question"],
                "answers": unique_answers or ["Noch keine Antwort"],
            }
        )
    return summary


def render_route_map_and_timeline(data, selected_photo_stop_name=None, map_key="route_photo_map"):
    map_route = data["map_route"]
    coastal_points = [point for point in map_route if point["kind"] == "coast"]
    inland_points = [point for point in map_route if point["kind"] != "coast"]
    route_points = [
        {
            **point,
            "position": [point["lon"], point["lat"]],
            "label": f"{index}. {point['name']}",
            "photo_count": "",
        }
        for index, point in enumerate(map_route, start=1)
    ]
    photo_stops = [
        {
            **stop,
            "position": [stop["lon"], stop["lat"]],
            "label_text": stop["name"],
            "photo_count": len(stop.get("photos", [])),
            "icon_data": {
                "url": photo_stop_icon_url(stop),
                "width": 72,
                "height": 72,
                "anchorY": 36,
            },
        }
        for stop in get_photo_stop_entries(data)
        if stop.get("photos")
    ]
    elephant_marker = {
        **data["map_elephant_marker"],
        "position": [data["map_elephant_marker"]["lon"], data["map_elephant_marker"]["lat"]],
        "label_text": "Addo Elephant Park",
        "photo_count": "",
        "icon_data": {
            "url": ELEPHANT_MAP_ICON_URL,
            "width": 72,
            "height": 72,
            "anchorY": 36,
        },
    }
    coastal_path = [{"name": "Küstenroute Cape Town → East London", "path": [[point["lon"], point["lat"]] for point in coastal_points]}]
    inland_path = [{"name": "✈️ Inland & Safari East London → Johannesburg → Kruger", "path": [[point["lon"], point["lat"]] for point in [coastal_points[-1], *inland_points]]}]

    route_map_state = st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(latitude=-29.2, longitude=25.2, zoom=3.75, pitch=0),
            layers=[
                pdk.Layer(
                    "PathLayer",
                    coastal_path,
                    get_path="path",
                    get_color=[0, 93, 115, 255],
                    width_min_pixels=8,
                    rounded=True,
                    pickable=True,
                ),
                pdk.Layer(
                    "PathLayer",
                    inland_path,
                    get_path="path",
                    get_color=[180, 108, 20, 255],
                    width_min_pixels=7,
                    rounded=True,
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
                    photo_stops,
                    get_icon="icon_data",
                    get_position="position",
                    get_size=1.5,
                    size_scale=16,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    photo_stops,
                    get_position="position",
                    get_text="label_text",
                    get_color=[31, 42, 36, 255],
                    get_size=13,
                    get_alignment_baseline="bottom",
                    get_pixel_offset=[0, -24],
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
        height=420,
        selection_mode="single-object",
        on_select="rerun",
        key=map_key,
    )
    st.caption("📷 Foto-Spot · 🍴 Restaurant/Food · 🍷 Aktivität · 🐘 Addo Elephant Park · Blau = Küstenroute · Gold = Inland/Safari. Tipp: Symbol antippen, um Fotos zu öffnen.")

    if photo_stops:
        photo_stop_names = {stop["name"] for stop in photo_stops}
        map_selected_photo_stop_name = None
        try:
            selected_objects = route_map_state.selection.get("objects", {})
            if isinstance(selected_objects, dict):
                object_groups = selected_objects.values()
            else:
                object_groups = [selected_objects]
            for layer_objects in object_groups:
                for selected_object in layer_objects:
                    if not isinstance(selected_object, dict):
                        continue
                    selected_name = selected_object.get("name") or selected_object.get("label_text")
                    if selected_name in photo_stop_names:
                        map_selected_photo_stop_name = selected_name
                        break
                if map_selected_photo_stop_name:
                    break
        except Exception:
            map_selected_photo_stop_name = None

        if map_selected_photo_stop_name:
            st.query_params["photo_stop"] = map_selected_photo_stop_name
            st.rerun()

        selected_photo_stop = next(
            (stop for stop in photo_stops if stop["name"] == selected_photo_stop_name),
            None,
        )
        if selected_photo_stop:
            st.markdown('<div id="foto-stopps"></div>', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(f"<p class=\"small\"><b>Foto-Stopp · {selected_photo_stop.get('location', selected_photo_stop['name'])}</b></p>", unsafe_allow_html=True)
                st.markdown(f"### {selected_photo_stop['name']}")
                st.write(selected_photo_stop.get("summary", "Bilder von diesem Reisestopp."))
                render_image_carousel(selected_photo_stop["photos"], "route-photo-stop-gallery")

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


def render_photo_map(data, map_key="photo_map"):
    photo_stops = [
        {
            **stop,
            "position": [stop["lon"], stop["lat"]],
            "label_text": stop["name"],
            "photo_count": len(stop.get("photos", [])),
            "icon_data": {
                "url": photo_stop_icon_url(stop),
                "width": 72,
                "height": 72,
                "anchorY": 36,
            },
        }
        for stop in get_photo_stop_entries(data)
        if stop.get("photos")
    ]
    if not photo_stops:
        st.info("Noch keine Foto-Stopps hinterlegt.")
        return

    map_state = st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(latitude=-27.2, longitude=23.7, zoom=3.05, pitch=0),
            layers=[
                pdk.Layer(
                    "IconLayer",
                    photo_stops,
                    get_icon="icon_data",
                    get_position="position",
                    get_size=1.5,
                    size_scale=20,
                    pickable=True,
                ),
                pdk.Layer(
                    "TextLayer",
                    photo_stops,
                    get_position="position",
                    get_text="label_text",
                    get_color=[31, 42, 36, 255],
                    get_size=14,
                    get_alignment_baseline="bottom",
                    get_pixel_offset=[0, -28],
                ),
            ],
            tooltip={"html": "<b>{name}</b><br>{photo_count} Fotos", "style": {"backgroundColor": "#315c45", "color": "#fffaf1"}},
        ),
        use_container_width=True,
        height=420,
        selection_mode="single-object",
        on_select="rerun",
        key=map_key,
    )
    st.caption("📷 Foto-Spot · 🍴 Restaurant/Food · 🍷 Aktivität · Symbol antippen, um die Fotos zu öffnen.")

    selected_photo_stop_name = None
    try:
        selected_objects = map_state.selection.get("objects", {})
        object_groups = selected_objects.values() if isinstance(selected_objects, dict) else [selected_objects]
        photo_stop_names = {stop["name"] for stop in photo_stops}
        for layer_objects in object_groups:
            for selected_object in layer_objects:
                if not isinstance(selected_object, dict):
                    continue
                selected_name = selected_object.get("name") or selected_object.get("label_text")
                if selected_name in photo_stop_names:
                    selected_photo_stop_name = selected_name
                    break
            if selected_photo_stop_name:
                break
    except Exception:
        selected_photo_stop_name = None

    if selected_photo_stop_name:
        st.query_params.clear()
        st.query_params["photo_stop"] = selected_photo_stop_name
        st.rerun()


data = load_data()
quiz = data.get("quiz", {})
quiz_questions = quiz.get("questions", []) if isinstance(quiz, dict) else quiz
photo_stops_data = get_photo_stop_entries(data)
selected_photo_stop_name = st.query_params.get("photo_stop")
selected_page = st.query_params.get("page")
selected_route_stop_name = st.query_params.get("stop")
selected_recommendation = st.query_params.get("recommendation")


def open_section(page=None, *, photo_stop=None, stop=None, recommendation=None):
    st.query_params.clear()
    if page:
        st.query_params["page"] = page
    if photo_stop:
        st.query_params["photo_stop"] = photo_stop
    if stop:
        st.query_params["stop"] = stop
    if recommendation:
        st.query_params["recommendation"] = recommendation
    st.rerun()


def render_back_to_overview():
    if st.button("← Zurück zur Reiseübersicht", key="back_to_overview", use_container_width=True):
        open_section()


with st.sidebar:
    st.title("🌍 Südafrika")
    st.markdown("### Menü")
    if st.button("🏠 Übersicht", key="nav_home", use_container_width=True):
        open_section()
    with st.expander("🦁 Freunde-Quiz", expanded=selected_page in {"quiz", "answers"}):
        if st.button("Quiz ansehen", key="nav_quiz", use_container_width=True):
            open_section("quiz")
        if st.button("Bisherige Antworten", key="nav_answers", use_container_width=True):
            open_section("answers")
    with st.expander("🗺️ Route & Etappen", expanded=selected_page == "route"):
        if st.button("Route ansehen", key="nav_route", use_container_width=True):
            open_section("route")
    if photo_stops_data:
        with st.expander("📷 Fotos", expanded=selected_page == "photo_map" or bool(selected_photo_stop_name)):
            if st.button("📍 Fotokarte ansehen", key="nav_photo_map", use_container_width=True):
                open_section("photo_map")

            grouped_photo_stops = {}
            for photo_stop in photo_stops_data:
                grouped_photo_stops.setdefault(photo_stop.get("region", "Weitere Spots"), []).append(photo_stop)

            for region, region_photo_stops in grouped_photo_stops.items():
                region_anchor = route_stop_anchor(region)
                region_state_key = f"nav_photo_region_open_{region_anchor}"
                region_is_active = any(stop["name"] == selected_photo_stop_name for stop in region_photo_stops)

                if region_state_key not in st.session_state:
                    st.session_state[region_state_key] = region_is_active
                elif region_is_active:
                    st.session_state[region_state_key] = True

                is_region_open = st.session_state[region_state_key]
                region_icon = "▼" if is_region_open else "▶"
                if st.button(f"{region_icon} {region}", key=f"nav_photo_region_button_{region_anchor}", use_container_width=True):
                    st.session_state[region_state_key] = not is_region_open
                    st.rerun()

                if st.session_state[region_state_key]:
                    for photo_stop in region_photo_stops:
                        icon = photo_stop_menu_icon(photo_stop)
                        if st.button(f"   {icon} {photo_stop['name']}", key=f"nav_photo_{route_stop_anchor(photo_stop['name'])}", use_container_width=True):
                            open_section(photo_stop=photo_stop["name"])
    with st.expander("⭐ Top Empfehlungen", expanded=selected_page == "recommendations"):
        if st.button("Restaurant", key="nav_recommendation_restaurant", use_container_width=True):
            open_section("recommendations", recommendation="restaurant")
        if st.button("Unterkunft", key="nav_recommendation_stay", use_container_width=True):
            open_section("recommendations", recommendation="stay")
        if st.button("Aktivitäten", key="nav_recommendation_activities", use_container_width=True):
            open_section("recommendations", recommendation="activities")
    st.divider()
    with st.expander("🔒 Privater Ordner", expanded=False):
        render_private_upload_folder()

if selected_photo_stop_name:
    selected_photo_page = next(
        (stop for stop in photo_stops_data if stop["name"] == selected_photo_stop_name),
        None,
    )
    if selected_photo_page:
        st.markdown('<div id="foto-stopps"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="hero">
          <span class="badge">📷 Foto-Stopp</span>
          <h1>Reisefotos</h1>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        with st.container(border=True):
            st.markdown(f"<p class=\"small\"><b>{selected_photo_page.get('location', selected_photo_page['name'])}</b></p>", unsafe_allow_html=True)
            st.markdown(f"### {selected_photo_page['name']}")
            st.write(selected_photo_page.get("summary", "Bilder von diesem Reisestopp."))
            render_image_carousel(
                selected_photo_page["photos"],
                "photo-stop-page-gallery",
                autoplay_ms=6000,
                object_fit="contain",
                height_px=430,
            )
        render_back_to_overview()
        st.stop()

if selected_page:
    restaurants_page = data.get("restaurants") or [data["restaurant"]]
    stays_page = data.get("stays") or [data["stay"]]
    activities_page = data.get("activities", [])

    if selected_page == "quiz":
        st.markdown("""
        <div class="hero">
          <span class="badge">🦁 Freunde-Quiz</span>
          <h1>Vorhersage abgeben</h1>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if quiz_questions:
            st.subheader(f"🧠 {quiz.get('title', 'Südafrika-Quiz') if isinstance(quiz, dict) else 'Südafrika-Quiz'}")
            st.caption(quiz.get("description", "Keine richtigen oder falschen Antworten – hier tippen deine Freunde, was unterwegs passiert.") if isinstance(quiz, dict) else "Keine richtigen oder falschen Antworten – hier tippen deine Freunde, was unterwegs passiert.")
            st.markdown("**Dein Name**")
            friend_name = st.text_input("Dein Name", placeholder="z. B. Anna", label_visibility="collapsed", key="quiz_page_name")
            answers = []
            answered_count = 0
            for index, question in enumerate(quiz_questions, start=1):
                options = ["– bitte wählen –", *question["options"]]
                answer = st.radio(f"{index}. {question['question']}", options, index=0, key=f"quiz_page_answer_{index}")
                if answer != "– bitte wählen –":
                    answered_count += 1
                answers.append(answer)
            st.progress(answered_count / len(quiz_questions), text=f"{answered_count} von {len(quiz_questions)} Tipps abgegeben")
            button_label = quiz.get("button_label", "Unsere Tipps speichern") if isinstance(quiz, dict) else "Unsere Tipps speichern"
            if st.button(button_label, type="primary", disabled=answered_count < len(quiz_questions) or st.session_state.get("quiz_page_checked", False), key="quiz_page_submit"):
                display_name = friend_name.strip() or "Anonym"
                save_quiz_result(display_name, quiz_questions, answers)
                results = get_all_quiz_results()
                notification_status = notify_quiz_submission(display_name, quiz_questions, answers)
                st.session_state["quiz_page_checked"] = True
                st.session_state["quiz_last_name"] = display_name
                st.session_state["quiz_last_answers"] = answers
                st.session_state["quiz_results"] = results
                st.session_state["quiz_notification_status"] = notification_status
            if st.session_state.get("quiz_page_checked"):
                display_name = st.session_state.get("quiz_last_name", friend_name.strip() or "Anonym")
                submitted_answers = st.session_state.get("quiz_last_answers", answers)
                results = st.session_state.get("quiz_results", get_all_quiz_results())
                st.success("Danke! Deine Vorhersage wurde gespeichert.")
                result_view = st.selectbox("Quiz Ergebnis anzeigen", ["Deine Antworten", "Bisher gewählte Antworten"], key="quiz_page_result_view")
                if result_view == "Deine Antworten":
                    for answer, question in zip(submitted_answers, quiz_questions):
                        st.markdown(f'<div class="quiz-answer">🦁 <strong>{question["question"]}</strong><br><span class="small">Tipp: {answer}</span></div>', unsafe_allow_html=True)
                else:
                    for item in summarize_quiz_results(results, quiz_questions):
                        answer_lines = "<br>".join(f"• {answer}" for answer in item["answers"])
                        st.markdown(f'<div class="quiz-answer">📝 <strong>{item["question"]}</strong><br><span class="small">{answer_lines}</span></div>', unsafe_allow_html=True)
        render_back_to_overview()
        st.stop()

    if selected_page == "answers":
        st.markdown("""
        <div class="hero">
          <span class="badge">🦁 Freunde-Quiz</span>
          <h1>Bisherige Antworten</h1>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        render_quiz_answer_summary(quiz_questions)
        render_back_to_overview()
        st.stop()

    if selected_page == "route":
        st.markdown("""
        <div class="hero">
          <span class="badge">🗺️ Route & Etappen</span>
          <h1>Reiseroute</h1>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        render_route_map_and_timeline(data, selected_photo_stop_name, map_key="route_page_map")
        render_back_to_overview()
        st.stop()

    if selected_page == "photo_map":
        st.markdown("""
        <div class="hero">
          <span class="badge">📍 Fotokarte</span>
          <h1>Foto-Stopps auf der Karte</h1>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        render_photo_map(data, map_key="photo_map_page")
        render_back_to_overview()
        st.stop()

    if selected_page == "recommendations":
        titles = {"restaurant": "Restaurant", "stay": "Unterkunft", "activities": "Aktivitäten"}
        current = selected_recommendation or "restaurant"
        st.markdown(f"""
        <div class="hero">
          <span class="badge">⭐ Top Empfehlungen</span>
          <h1>{titles.get(current, 'Top Empfehlungen')}</h1>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        if current == "restaurant":
            for index, restaurant_item in enumerate(restaurants_page):
                with st.container(border=True):
                    st.markdown(f"<p class=\"small\"><b>Restaurant · {restaurant_item.get('location', '')}</b></p>", unsafe_allow_html=True)
                    st.markdown(f"### {restaurant_item['name']}")
                    gallery_images = restaurant_item.get("images") or ([restaurant_item["image"]] if restaurant_item.get("image") else [])
                    if gallery_images:
                        render_image_carousel(gallery_images, f"restaurant-page-carousel-{index}", object_fit="contain", height_px=430)
                    st.write(restaurant_item["why"])
                    if restaurant_item.get("tip"):
                        st.caption(restaurant_item["tip"])
                    if restaurant_item.get("link"):
                        st.link_button("Restaurant öffnen", restaurant_item["link"], key=f"restaurant_page_link_{index}")
        elif current == "stay":
            for index, stay_item in enumerate(stays_page):
                with st.container(border=True):
                    st.markdown(f"<p class=\"small\"><b>Unterkunft · {stay_item.get('location', '')}</b></p>", unsafe_allow_html=True)
                    st.markdown(f"### {stay_item['name']}")
                    gallery_images = stay_item.get("images") or ([stay_item["image"]] if stay_item.get("image") else [])
                    if gallery_images:
                        render_image_carousel(gallery_images, f"stay-page-carousel-{index}")
                    st.write(stay_item["why"])
                    if stay_item.get("tip"):
                        st.caption(stay_item["tip"])
                    if stay_item.get("link"):
                        st.link_button("Unterkunft öffnen", stay_item["link"], key=f"stay_page_link_{index}")
        else:
            if activities_page:
                for index, activity in enumerate(activities_page):
                    with st.container(border=True):
                        st.markdown(f"<p class=\"small\"><b>Aktivität · {activity.get('location', '')}</b></p>", unsafe_allow_html=True)
                        st.markdown(f"### {activity['name']}")
                        gallery_images = activity.get("images") or ([activity["image"]] if activity.get("image") else [])
                        if gallery_images:
                            render_image_carousel(gallery_images, f"activity-page-carousel-{index}", object_fit="contain", height_px=430)
                        st.write(activity.get('why', 'Ausgewählte Aktivität für die Reise.'))
                        if activity.get("tip"):
                            st.caption(activity["tip"])
                        if activity.get("link"):
                            st.link_button("Aktivität öffnen", activity["link"], key=f"activity_page_link_{index}")
            else:
                with st.container(border=True):
                    st.markdown("### Noch offen")
                    st.write("Hier ergänzen wir schöne Ausflüge, Aussichtspunkte und besondere Stopps.")
        render_back_to_overview()
        st.stop()

st.markdown("""
<div class="hero">
  <span class="badge">Cape Town → East London → Johannesburg → Kruger</span>
  <h1>Südafrika Reise</h1>
</div>
""", unsafe_allow_html=True)

st.write("")

show_quiz_answers = st.query_params.get("show") == "answers"

if st.query_params.get("show") == "quiz":
    st.session_state["show_friend_quiz"] = True

st.write("")
st.markdown('<div id="freunde-quiz"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="quiz-teaser">
  <div>
    <h2><span class="emoji">🦁</span>Freunde-Quiz</h2>
    <p>Was glaubt ihr, was auf unserer Südafrika-Reise passieren wird?</p>
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

    button_label = quiz.get("button_label", "Unsere Tipps speichern") if isinstance(quiz, dict) else "Unsere Tipps speichern"
    if st.button(button_label, type="primary", disabled=answered_count < len(quiz_questions) or st.session_state.get("quiz_checked", False)):
        display_name = friend_name.strip() or "Anonym"
        save_quiz_result(display_name, quiz_questions, answers)
        results = get_all_quiz_results()
        notification_status = notify_quiz_submission(display_name, quiz_questions, answers)
        st.session_state["quiz_checked"] = True
        st.session_state["quiz_last_name"] = display_name
        st.session_state["quiz_last_answers"] = answers
        st.session_state["quiz_results"] = results
        st.session_state["quiz_notification_status"] = notification_status

    if st.session_state.get("quiz_checked"):
        display_name = st.session_state.get("quiz_last_name", friend_name.strip() or "Anonym")
        submitted_answers = st.session_state.get("quiz_last_answers", answers)
        results = st.session_state.get("quiz_results", get_all_quiz_results())
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

st.markdown('<div id="route-etappen"></div>', unsafe_allow_html=True)
st.subheader("🗺️ Route & Etappen")
render_route_map_and_timeline(data, selected_photo_stop_name, map_key="route_photo_map")

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
        with st.container(border=True):
            st.markdown(f"<p class=\"small\"><b>Restaurant · {restaurant_item.get('location', '')}</b></p>", unsafe_allow_html=True)
            st.markdown(f"### {restaurant_item['name']}")
            st.write(restaurant_item["why"])
            if restaurant_item.get("tip"):
                st.caption(restaurant_item["tip"])
            if restaurant_item.get("link"):
                st.link_button("Restaurant öffnen", restaurant_item["link"], key=f"restaurant_link_{index}")
with r2:
    st.markdown('<div id="top-unterkunft"></div>', unsafe_allow_html=True)
    for index, stay_item in enumerate(stays):
        with st.container(border=True):
            st.markdown(f"<p class=\"small\"><b>Unterkunft · {stay_item.get('location', '')}</b></p>", unsafe_allow_html=True)
            st.markdown(f"### {stay_item['name']}")
            gallery_images = stay_item.get("images") or ([stay_item["image"]] if stay_item.get("image") else [])
            if gallery_images:
                render_image_carousel(gallery_images, f"stay-carousel-{index}")
            st.write(stay_item["why"])
            if stay_item.get("tip"):
                st.caption(stay_item["tip"])
            if stay_item.get("link"):
                st.link_button("Unterkunft öffnen", stay_item["link"], key=f"stay_link_{index}")
with r3:
    st.markdown('<div id="top-aktivitaeten"></div>', unsafe_allow_html=True)
    if activities:
        activity = activities[0]
        with st.container(border=True):
            st.markdown('<p class="small"><b>Aktivitäten</b></p>', unsafe_allow_html=True)
            st.markdown(f"### {activity['name']}")
            st.write(activity.get('why', 'Ausgewählte Aktivität für die Reise.'))
            if activity.get("tip"):
                st.caption(activity["tip"])
            if activity.get("link"):
                st.link_button("Aktivität öffnen", activity["link"])
    else:
        with st.container(border=True):
            st.markdown('<p class="small"><b>Aktivitäten</b></p>', unsafe_allow_html=True)
            st.markdown("### Noch offen")
            st.write("Hier ergänzen wir schöne Ausflüge, Aussichtspunkte und besondere Stopps.")

