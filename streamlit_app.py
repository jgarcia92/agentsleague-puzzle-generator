import json
import streamlit as st

from puzzle_generator import generate_puzzles, DIFFICULTIES, CATEGORIES


st.set_page_config(page_title="Puzzle Generator", page_icon="🧩", layout="centered")


def main():
    # AI-Assisted by Copilot: Initial Streamlit scaffold and layout
    st.title("🧩 Puzzle Generator – Streamlit UI")
    st.caption("Creative Apps Track · Built with GitHub Copilot")

    with st.sidebar:
        st.header("Controls")
        count = st.number_input("How many puzzles?", min_value=1, max_value=50, value=5)
        difficulty = st.selectbox("Difficulty", DIFFICULTIES, index=DIFFICULTIES.index("medium"))
        category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index("general"))
        output_format = st.radio("Format", ["text", "json"], index=0, horizontal=True)
        generate = st.button("Generate Puzzles", type="primary")

    if generate:
        try:
            puzzles = generate_puzzles(count=count, difficulty=difficulty, category=category)

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
                    with st.expander(f"Puzzle {i}: {p.get('category','general').title()} ({p.get('difficulty','medium').upper()})", expanded=True):
                        st.write("**Question:**", p["question"]) 
                        st.info(p["answer"], icon="💡")

        except ValueError as e:
            st.error(f"{e}")


if __name__ == "__main__":
    main()
