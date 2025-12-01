import streamlit as st
import random
import json
import os
from datetime import datetime

# ========== Utility Functions ==========

SCOREFILE = "scores.json"

def load_scores():
    if os.path.exists(SCOREFILE):
        with open(SCOREFILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(data):
    with open(SCOREFILE, "w") as f:
        json.dump(data, f, indent=4)

def reset_game():
    """Start or restart a new round."""
    category = random.choice(list(CATEGORIES.keys()))
    word = random.choice(CATEGORIES[category])
    st.session_state.word = word
    st.session_state.hint = category
    st.session_state.display = ["_"] * len(word)
    st.session_state.lives = 6
    st.session_state.guessed = []
    st.session_state.feedback = ""
    st.session_state.round_finished = False

# ========== Game Data ==========

CATEGORIES = {
    "fruits 🍎": ["apple", "banana", "orange", "mango", "grapes", "pineapple"],
    "animals 🐾": ["tiger", "lion", "elephant", "zebra", "monkey", "giraffe"],
    "countries 🌍": ["pakistan", "canada", "france", "japan", "brazil", "italy"],
    "cities 🏙️": ["paris", "karachi", "london", "tokyo", "dubai", "newyork"],
    "vegetables 🥕": ["carrot", "potato", "onion", "tomato", "cabbage", "broccoli"],
    "languages 💻": ["python", "java", "english", "urdu", "arabic", "french"]
}

# ========== Page Setup ==========

st.set_page_config(page_title="Quiz Guess - Game", page_icon="", layout="wide")

# ========== Navigation ==========

page = st.sidebar.radio("Navigation", ["🎮 Play Game", "🔐 Admin Panel"])

if page == "🎮 Play Game":
    st.title("Quiz Guess Game")
    st.write("Guess the hidden word — enter one alphabet letter per turn!")

    # ========== Load Data ==========

    if "scores" not in st.session_state:
        st.session_state.scores = load_scores()

    # ========== Player Login ==========

    if "player_name" not in st.session_state:
        name = st.text_input("Enter your name to start:", key="player_name_input")
        if st.button("Start Game"):
            if not name.strip():
                st.warning("Please enter a valid name.")
            else:
                st.session_state.player_name = name.strip()
                if name not in st.session_state.scores:
                    st.session_state.scores[name] = {"wins": 0, "losses": 0, "score": 0}
                    save_scores(st.session_state.scores)
                reset_game()
                st.rerun()
        st.stop()

    player = st.session_state.player_name

    # ========== Sidebar Info ==========

    st.sidebar.title("🏆 Player Stats")
    pdata = st.session_state.scores[player]
    st.sidebar.write(f"👤 **{player}**")
    st.sidebar.write(f"⭐ Score: **{pdata['score']}**")
    st.sidebar.write(f"✅ Wins: **{pdata['wins']}**")
    st.sidebar.write(f"❌ Losses: **{pdata['losses']}**")

    st.sidebar.subheader("🌍 Leaderboard")
    sorted_scores = sorted(st.session_state.scores.items(), key=lambda x: x[1]["score"], reverse=True)
    for i, (n, d) in enumerate(sorted_scores[:5], start=1):
        st.sidebar.write(f"{i}. **{n}** — {d['score']} pts")

    if st.sidebar.button("🔁 Logout"):
        del st.session_state["player_name"]
        st.rerun()
        
    # ========== Game Interface ==========

    if "word" not in st.session_state:
        reset_game()

    if "round_finished" not in st.session_state:
        st.session_state.round_finished = False
    st.progress(st.session_state.lives / 6)

    if st.session_state.feedback:
        msg = st.session_state.feedback
        if msg.startswith("✅"):
            st.success(msg)
        elif msg.startswith("❌"):
            st.error(msg)
        elif msg.startswith("⚠️"):
            st.warning(msg)

    st.markdown(f"### Word: **{' '.join(st.session_state.display)}**")
    st.write(f"Lives left: ❤️ **{st.session_state.lives} / 6**")
    st.write(f"Guessed letters: `{', '.join(st.session_state.guessed)}`")
    st.write(f"💡 Hint: The word is related to **{st.session_state.hint}**")

    # ========== Guess Input (Autofocus Fixed) ==========

    st.markdown(
        """
        <script>
        const box = window.parent.document.querySelector('input[id="guess_input"]');
        if (box) { box.focus(); }
        </script>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.round_finished:
        with st.form("guess_form", clear_on_submit=True):
            guess = st.text_input("Enter a letter:", max_chars=1, key="guess_input").lower().strip()
            submit = st.form_submit_button("Guess")

        if submit:
            if not guess:
                st.session_state.feedback = "⚠️ Please enter a letter!"
                st.rerun()
            elif not guess.isalpha():
                st.session_state.feedback = "⚠️ Enter only alphabets (A–Z)."
                st.rerun()
            elif len(guess) != 1:
                st.session_state.feedback = "⚠️ Enter a single letter."
                st.rerun()
            elif guess in st.session_state.guessed:
                st.session_state.feedback = "⚠️ You already guessed that letter!"
                st.rerun()
            else:
                st.session_state.guessed.append(guess)
                if guess in st.session_state.word:
                    for i, letter in enumerate(st.session_state.word):
                        if letter == guess:
                            st.session_state.display[i] = guess
                    st.session_state.feedback = "✅ Correct guess!"
                    st.session_state.scores[player]["score"] += 1
                else:
                    st.session_state.lives -= 1
                    st.session_state.feedback = "❌ Wrong guess!"
            save_scores(st.session_state.scores)
            st.rerun()

    # ========== Win / Lose ==========

    if "_" not in st.session_state.display and not st.session_state.round_finished:
        st.session_state.round_finished = True
        st.success(f"🎉 You won! The word was **{st.session_state.word}**.")
        st.session_state.scores[player]["wins"] += 1
        st.session_state.scores[player]["score"] += 10
        save_scores(st.session_state.scores)

    if st.session_state.lives == 0 and not st.session_state.round_finished:
        st.session_state.round_finished = True
        st.error(f"💀 You lost! The word was **{st.session_state.word}**.")
        st.session_state.scores[player]["losses"] += 1
        save_scores(st.session_state.scores)

    # ========== Play Again Button ==========

    if st.session_state.round_finished:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎮 Play Again"):
                reset_game()
                st.rerun()
        with col2:
            if st.button("🏁 Exit Game"):
                del st.session_state["player_name"]
                st.rerun()

elif page == "🔐 Admin Panel":
    st.title("")
    st.write("")
    
    # ========== Admin Authentication ==========

    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    
    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False
    
    if not st.session_state.admin_logged_in:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            
            username = st.text_input("Username:", key="admin_user")
            password = st.text_input("Password:", type="password", key="admin_pass")
            
            if st.button("Login"):
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials!")
    else:
        if st.sidebar.button("🚪 Logout Admin"):
            st.session_state.admin_logged_in = False
            st.rerun()
        
        # ========== Admin Dashboard ==========

        tab1, tab2, tab3 = st.tabs(["📝 Add Words", "📋 View Words", "🗑️ Remove Words"])
        
        with tab1:
            st.subheader("➕ Add New Words")
            category = st.selectbox("Select Category:", list(CATEGORIES.keys()))
            new_word = st.text_input("Enter new word:").lower().strip()
            
            if st.button("Add Word"):
                if new_word and new_word.isalpha():
                    if new_word not in CATEGORIES[category]:
                        CATEGORIES[category].append(new_word)
                        with open("categories.json", "w") as f:
                            json.dump(CATEGORIES, f, indent=4)
                        st.success(f"✅ Word '{new_word}' added to {category}!")
                    else:
                        st.warning("⚠️ Word already exists!")
                else:
                    st.error("❌ Enter a valid word (letters only)!")
        
        with tab2:
            st.subheader("📋 View All Words")
            for cat, words in CATEGORIES.items():
                st.write(f"**{cat}:** {', '.join(words)}")
        
        with tab3:
            st.subheader("🗑️ Remove Words")
            category = st.selectbox("Select Category:", list(CATEGORIES.keys()), key="remove_cat")
            word_to_remove = st.selectbox("Select word to remove:", CATEGORIES[category])
            
            if st.button("Remove Word"):
                CATEGORIES[category].remove(word_to_remove)
                with open("categories.json", "w") as f:
                    json.dump(CATEGORIES, f, indent=4)
                st.success(f"✅ Word '{word_to_remove}' removed!")
                st.rerun()
