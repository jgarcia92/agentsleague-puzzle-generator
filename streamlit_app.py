import json
import os
import streamlit as st

from puzzle_generator import generate_puzzles, DIFFICULTIES, CATEGORIES
from config import get_provider, get_api_keys, validate_keys


st.set_page_config(page_title="Puzzle Generator", page_icon="🧩", layout="wide")


def main():
    # AI-Assisted by Copilot: Initial Streamlit scaffold and layout
    st.title("🧩 Puzzle Generator – Streamlit UI")
    st.caption("Creative Apps Track · Built with GitHub Copilot")

    # Main content area placeholder
    hero = st.container()
    results = st.container()

    with st.sidebar:
        st.header("Provider & Keys")
        # Provider selection
        current_provider = get_provider()
        provider = st.selectbox("Model provider", ["none", "openai", "gemini"], index=["none","openai","gemini"].index(current_provider))

        # Key inputs (masked). Keys are stored in session and env for the current run only.
        if provider == "openai":
            default_key = st.session_state.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
            openai_key = st.text_input("OpenAI API Key", value=default_key, type="password", placeholder="sk-...")
            apply_keys = st.button("Apply Key", key="apply_openai")
            if apply_keys:
                if openai_key:
                    os.environ["OPENAI_API_KEY"] = openai_key
                    st.session_state["OPENAI_API_KEY"] = openai_key
                    st.success("OpenAI key applied for this session.")
                else:
                    st.warning("No key entered.")
        elif provider == "gemini":
            default_key = st.session_state.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
            gemini_key = st.text_input("Gemini API Key", value=default_key, type="password", placeholder="AIza...")
            apply_keys = st.button("Apply Key", key="apply_gemini")
            if apply_keys:
                if gemini_key:
                    os.environ["GOOGLE_API_KEY"] = gemini_key
                    st.session_state["GOOGLE_API_KEY"] = gemini_key
                    st.success("Gemini key applied for this session.")
                else:
                    st.warning("No key entered.")
        else:
            st.caption("Provider set to none – keys not required.")

        ok, msg = validate_keys()
        st.status("Ready" if ok else "Missing key", state="complete" if ok else "error")
        with st.popover("Security note"):
            st.write("Keys entered here are used only for this running session and are not saved to disk. For permanent config, edit .env locally.")

        st.divider()
        st.header("Controls")
        count = st.number_input("How many puzzles?", min_value=1, max_value=50, value=5)
        difficulty = st.selectbox("Difficulty", DIFFICULTIES, index=DIFFICULTIES.index("medium"))
        category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index("general"))
        output_format = st.radio("Format", ["text", "json"], index=0, horizontal=True)
        auto = st.toggle("Generate on load", value=True, help="Create puzzles automatically on first load")
        generate = st.button("Generate Puzzles", type="primary")

    # Generate by user action or first load (session-scoped)
    if auto and not st.session_state.get("_auto_generated", False):
        st.session_state["_auto_generated"] = True
        generate = True

    if generate:
        try:
            puzzles = generate_puzzles(count=count, difficulty=difficulty, category=category)

            with results:
                st.subheader("Results")
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
                        st.markdown(f"**Puzzle {i}:** {p.get('category','general').title()} · {p.get('difficulty','medium').upper()}")
                        st.write(p["question"]) 
                        with st.expander("Show answer", expanded=False):
                            st.info(p["answer"], icon="💡")
                        st.divider()

        except ValueError as e:
            st.error(f"{e}")
    else:
        # Initial hero/empty state
        with hero:
            st.subheader("Welcome 👋")
            st.write("Use the controls on the left to generate puzzles, or keep 'Generate on load' enabled to see examples automatically.")
            st.caption("Tip: switch to JSON to download the generated set.")


if __name__ == "__main__":
    main()
