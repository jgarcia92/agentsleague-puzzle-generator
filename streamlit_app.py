import json
import os
from io import BytesIO

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import random
import re

from puzzle_generator import generate_puzzles, DIFFICULTIES, CATEGORIES
from config import get_provider, validate_keys


# Visual palette and emojis per category
CATEGORY_COLORS = {
    "general": (99, 102, 241),   # indigo
    "logic": (16, 185, 129),     # emerald
    "math": (245, 158, 11),      # amber
    "wordplay": (236, 72, 153),  # pink
}

EMOJI = {
    "general": "💡",
    "logic": "🧩",
    "math": "➗",
    "wordplay": "🔤",
}


def make_hint(answer: str, category: str) -> list[str]:
    """Return 3 short, randomized hints based on the answer and category."""
    ans = (answer or "").strip()
    letters = [c for c in ans if c.isalpha()]
    words = [w for w in ans.split() if w]
    uniq_letters = sorted(set([c.upper() for c in letters]))

    structural: list[str] = []
    if letters:
        structural.append(f"Starts with: {letters[0].upper()}")
        structural.append(f"Ends with: {letters[-1].upper()}")
        structural.append(f"Letters: {len(letters)}")
        # Vowels/consonants if applicable
        vowels = sum(1 for c in letters if c.lower() in "aeiou")
        consonants = len(letters) - vowels
        if vowels:
            structural.append(f"Vowels: {vowels}")
        if consonants:
            structural.append(f"Consonants: {consonants}")
        # Random contains letter
        if uniq_letters:
            pick = random.choice(uniq_letters)
            structural.append(f"Contains: {pick}")
    if words:
        structural.append(f"Words: {len(words)}")
        if len(words) > 1:
            structural.append(f"Words: {len(words)} · Letters: {len(letters)}")

    category_tips = {
        "logic": [
            "Think process of elimination",
            "Consider order and state changes",
            "Test simple cases first",
        ],
        "math": [
            "Estimate before you compute",
            "Watch units and totals",
            "Look for symmetry",
        ],
        "wordplay": [
            "Listen to sounds, not spelling",
            "Homophones might help",
            "Think prefixes and suffixes",
        ],
        "general": [
            "Lateral thinking helps",
            "Focus on the key noun",
            "Rephrase the question",
        ],
    }

    # Always include exactly one category tip and 2 random structural hints (if available)
    tip = random.choice(category_tips.get(category, ["Follow the clues closely"]))
    chosen: list[str] = []
    if structural:
        k = 2 if len(structural) >= 2 else 1
        chosen = random.sample(structural, k)
    chosen.append(tip)
    return chosen


def clue_image(puzzle_index: int, category: str, difficulty: str, answer: str) -> bytes:
    w, h = 960, 260
    base = Image.new("RGB", (w, h), (15, 15, 18))
    draw = ImageDraw.Draw(base)

    r, g, b = CATEGORY_COLORS.get(category, (99, 102, 241))
    for y in range(h):
        alpha = y / h
        color = (
            int(r * (1 - alpha) + 18 * alpha),
            int(g * (1 - alpha) + 18 * alpha),
            int(b * (1 - alpha) + 18 * alpha),
        )
        draw.line([(0, y), (w, y)], fill=color)

    try:
        font_title = ImageFont.truetype("arial.ttf", 44)
        font_hint = ImageFont.truetype("arial.ttf", 24)
        font_big = ImageFont.truetype("seguiemj.ttf", 64)
    except Exception:
        font_title = ImageFont.load_default()
        font_hint = ImageFont.load_default()
        font_big = ImageFont.load_default()

    title = f"Puzzle {puzzle_index}: {category.title()}"
    draw.text((28, 26), title, fill=(245, 245, 255), font=font_title)
    draw.text((28, 86), f"Difficulty: {difficulty.upper()}", fill=(235, 240, 240), font=font_hint)
    draw.text((820, 24), EMOJI.get(category, "💡"), fill=(255, 255, 255), font=font_big)

    y0 = 130
    for line in make_hint(answer, category):
        draw.text((28, y0), f"• {line}", fill=(235, 240, 240), font=font_hint)
        y0 += 28

    buf = BytesIO()
    base.save(buf, format="PNG")
    return buf.getvalue()


def _sdk_available(provider: str) -> bool:
    try:
        if provider == "openai":
            import openai  # type: ignore  # noqa: F401
        elif provider == "gemini":
            import google.generativeai as genai  # type: ignore  # noqa: F401
        return True
    except Exception:
        return False


def _safe_json_from_text(text: str):
    """Extract JSON array from raw LLM text, handling fenced code blocks."""
    if not text:
        return None
    s = text.strip()
    # Extract between triple backticks if present
    if "```" in s:
        parts = s.split("```")
        # try to find a json block
        for i in range(len(parts)):
            block = parts[i]
            if block.lstrip().lower().startswith("json"):
                candidate = parts[i + 1] if i + 1 < len(parts) else block
                s = candidate
                break
        else:
            # no explicit json tag; take the first fenced content
            s = parts[1] if len(parts) > 1 else s
    # Try direct JSON first
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            for key in ["items", "puzzles", "data", "result"]:
                if key in obj and isinstance(obj[key], list):
                    return obj[key]
        return obj
    except Exception:
        pass

    # Try to pull the first JSON array from the text
    m_start = s.find("[")
    m_end = s.rfind("]")
    if m_start != -1 and m_end != -1 and m_end > m_start:
        try:
            return json.loads(s[m_start:m_end + 1])
        except Exception:
            pass
    return None


def _generate_puzzles_via_ai(count: int, difficulty: str, category: str, provider: str):
    """Generate puzzles via OpenAI or Gemini; fallback to templates on failure."""
    count = max(1, min(int(count), 20))
    system = (
        "You create short, self-contained puzzles. "
        "Return ONLY strict JSON (no markdown). Schema: {\"items\": [ {\"question\": str, \"answer\": str, \"difficulty\": 'easy|medium|hard', \"category\": 'general|logic|math|wordplay' } ]}."
    )
    user = (
        f"Generate {count} unique puzzles for category='{category}' and difficulty='{difficulty}'. "
        "Each question 1-2 sentences max. Respond as a JSON object with an 'items' array only."
    )

    text = None
    if provider == "openai":
        try:
            try:
                from openai import OpenAI  # type: ignore
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    temperature=0.9,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                text = resp.choices[0].message.content
            except Exception:
                import openai  # type: ignore
                openai.api_key = os.getenv("OPENAI_API_KEY")
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    temperature=0.9,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                text = resp.choices[0].message["content"]
        except Exception as e:
            st.session_state["last_generation_source"] = "ai-failed-openai"
            st.warning(f"OpenAI call failed: {e}. Falling back to templates.")
    elif provider == "gemini":
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            model = genai.GenerativeModel("gemini-pro", generation_config={"response_mime_type": "application/json"})
            resp = model.generate_content(f"{system}\n\n{user}")
            text = getattr(resp, "text", None)
        except Exception as e:
            st.session_state["last_generation_source"] = "ai-failed-gemini"
            st.warning(f"Gemini call failed: {e}. Falling back to templates.")

    parsed = _safe_json_from_text(text or "")
    if isinstance(parsed, list) and parsed:
        # Normalize fields and clip to requested count; dedupe by question
        normalized = []
        seen_q = set()
        for item in parsed[:count]:
            if not isinstance(item, dict):
                continue
            q = str(item.get("question", "")).strip()
            a = str(item.get("answer", "")).strip()
            d = str(item.get("difficulty", difficulty)).lower()
            c = str(item.get("category", category)).lower()
            if not q or not a:
                continue
            key = q.lower()
            if key in seen_q:
                continue
            seen_q.add(key)
            normalized.append({
                "question": q,
                "answer": a,
                "difficulty": d if d in DIFFICULTIES else difficulty,
                "category": c if c in CATEGORIES else category,
            })
        # Randomize order for variety
        if normalized:
            random.shuffle(normalized)
        # Top up with templates if the model returned fewer unique items
        if len(normalized) < count:
            need = count - len(normalized)
            extras = generate_puzzles(count=need, difficulty=difficulty, category=category)
            # ensure uniqueness vs normalized
            for e in extras:
                if e["question"].lower() not in seen_q:
                    normalized.append(e)
                    seen_q.add(e["question"].lower())
                if len(normalized) >= count:
                    break
        if normalized:
            st.session_state["last_generation_source"] = f"ai-{provider}"
            return normalized[:count]

    # Fallback to local templates
    st.session_state["last_generation_source"] = "templates-fallback"
    return generate_puzzles(count=count, difficulty=difficulty, category=category)


def main():
    st.set_page_config(page_title="Puzzle Generator", page_icon="🧩", layout="wide")

    st.title("🧩 Puzzle Generator – AgentsLeague - CreativeApps")
    st.caption("Creative Apps Track · Built with GitHub Copilot")

    hero = st.container()
    results = st.container()

    with st.sidebar:
        st.header("Provider & Keys")
        current_provider = get_provider()
        provider = st.selectbox(
            "Model provider", ["none", "openai", "gemini"],
            index=["none", "openai", "gemini"].index(current_provider),
        )
        os.environ["MODEL_PROVIDER"] = provider
        st.session_state["MODEL_PROVIDER"] = provider

        if provider == "openai":
            default_key = st.session_state.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
            openai_key = st.text_input("OpenAI API Key", value=default_key, type="password", placeholder="sk-...")
            if st.button("Apply Key", key="apply_openai"):
                if openai_key:
                    os.environ["OPENAI_API_KEY"] = openai_key
                    st.session_state["OPENAI_API_KEY"] = openai_key
                    st.success("OpenAI key applied for this session.")
                else:
                    st.warning("No key entered.")
        elif provider == "gemini":
            default_key = st.session_state.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
            gemini_key = st.text_input("Gemini API Key", value=default_key, type="password", placeholder="AIza...")
            if st.button("Apply Key", key="apply_gemini"):
                if gemini_key:
                    os.environ["GOOGLE_API_KEY"] = gemini_key
                    st.session_state["GOOGLE_API_KEY"] = gemini_key
                    st.success("Gemini key applied for this session.")
                else:
                    st.warning("No key entered.")
        else:
            st.caption("Provider set to none – keys not required.")

        ok, msg = validate_keys()
        if provider == "none":
            st.caption("Using offline templates unless you switch to a provider.")
        elif ok:
            st.success("Provider and key are set. You can use AI generation.")
        else:
            st.warning(msg + " — falling back to templates if AI mode is chosen.")
        # Diagnostics
        with st.expander("Diagnostics", expanded=False):
            st.caption(f"SDK available: {'yes' if _sdk_available(provider) else 'no'}")
            masked = 'yes' if (os.getenv('OPENAI_API_KEY') or os.getenv('GOOGLE_API_KEY')) else 'no'
            st.caption(f"Key detected in session: {masked}")
        with st.popover("Security note"):
            st.write("Keys entered here are used only for this running session and are not saved to disk. For permanent config, edit .env locally.")

        st.divider()
        st.header("Controls")
        count = st.number_input("How many puzzles?", min_value=1, max_value=50, value=5)
        difficulty = st.selectbox("Difficulty", DIFFICULTIES, index=DIFFICULTIES.index("medium"))
        category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index("general"))
        output_format = st.radio("Format", ["text", "json"], index=0, horizontal=True)
        # Let users choose generation source. AI option visible even if keys missing; we'll fallback gracefully.
        mode_label = "AI model (OpenAI/Gemini)" if (provider in ("openai", "gemini")) else "AI model (enable provider to use)"
        gen_mode = st.radio(
            "Generation mode",
            ["Templates (offline)", mode_label],
            index=0,
        )
        use_ai = gen_mode.startswith("AI model") and (provider in ("openai", "gemini")) and ok
        auto = st.toggle("Generate on load", value=True, help="Create puzzles automatically on first load")
        generate = st.button("Generate Puzzles", type="primary")

    if auto and not st.session_state.get("_auto_generated", False):
        st.session_state["_auto_generated"] = True
        generate = True

    if generate:
        try:
            if use_ai:
                with st.spinner("Generating puzzles with AI…"):
                    puzzles = _generate_puzzles_via_ai(count=count, difficulty=difficulty, category=category, provider=provider)
            else:
                puzzles = generate_puzzles(count=count, difficulty=difficulty, category=category)
                st.session_state["last_generation_source"] = "templates"
            with results:
                st.subheader("Results")
                src = st.session_state.get("last_generation_source", "templates")
                if src.startswith("ai-"):
                    st.caption(f"Source: AI ({src.split('-')[-1]})")
                elif src == "templates-fallback":
                    st.caption("Source: Templates (AI requested but fell back)")
                    st.info("Couldn’t parse a valid response from the model; using templates instead.")
                else:
                    st.caption("Source: Templates (offline)")
                if output_format == "json":
                    st.code(json.dumps(puzzles, indent=2), language="json")
                    st.download_button(
                        label="Download JSON",
                        data=json.dumps(puzzles, indent=2),
                        file_name="puzzles.json",
                        mime="application/json",
                    )
                else:
                    for i, p in enumerate(puzzles, start=1):
                        cat = p.get("category", "general")
                        diff = p.get("difficulty", "medium")
                        img_bytes = clue_image(
                            puzzle_index=i,
                            category=cat,
                            difficulty=diff,
                            answer=p.get("answer", ""),
                        )
                        st.image(img_bytes)
                        st.markdown("**Question**")
                        st.write(p["question"])  
                        with st.expander("Show answer", expanded=False):
                            st.info(p["answer"], icon="💡")
                            st.button("Copy answer", key=f"copy_{i}", help="Copy not available in all browsers")
                        st.divider()
        except ValueError as e:
            st.error(f"{e}")
    else:
        with hero:
            st.subheader("Welcome 👋")
            st.write("Use the controls on the left to generate puzzles, or keep 'Generate on load' enabled to see examples automatically.")
            st.caption("Tip: switch to JSON to download the generated set.")


if __name__ == "__main__":
    main()
