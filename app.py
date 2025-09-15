import streamlit as st
import pandas as pd
import re
import sqlite3
import joblib

# ==================
# Load ML model & encoders
# ==================
model = joblib.load("model.pkl")
transformer = joblib.load("transformer.pkl")
label_encoder = joblib.load("label_encoder.pkl")

# ==================
# SQLite connection
# ==================
conn = sqlite3.connect("user_data.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS user_info (
    username TEXT,
    password TEXT,
    name TEXT,
    gender TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    mobile_prediction TEXT,
    rating INTEGER,
    feedback TEXT
)
""")
conn.commit()

# ==================
# Session state setup
# ==================
if "page" not in st.session_state:
    st.session_state.page = 1

if "form_data" not in st.session_state:
    st.session_state.form_data = {}

if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False

# ==================
# Custom CSS
# ==================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #74ebd5, #acb6e5);
}
h2 {
    text-align: center;
    color: white !important;
    background-color: rgba(0,0,0,0.4);
    padding: 10px;
    border-radius: 10px;
}
div.stButton > button {
    background-color: #ff7f50;
    color: white;
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    padding: 10px 20px;
}
div.stButton > button:hover {
    background-color: #ff5722;
    color: white;
}
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stTextArea > div > div > textarea {
    border-radius: 8px;
    border: 2px solid #ff7f50;
}
.stSlider > div > div > div {
    background: #ff7f50;
}
</style>
""", unsafe_allow_html=True)

# ==================
# Navigation helpers
# ==================
def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

# ==================
# PAGE 1 – LOGIN
# ==================
if st.session_state.page == 1:
    st.markdown("<h2>🔑 Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username (Gmail or Phone)", max_chars=16,
                             value=st.session_state.form_data.get("username", ""))
    password = st.text_input("Password", type="password", max_chars=8,
                             value=st.session_state.form_data.get("password", ""))

    if st.button("Next ➡"):
        username_valid = (
            re.match(r"^[\w\.-]+@gmail\.com$", username) or
            re.match(r"^\d{10}$", username)
        )
        password_valid = (
            re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8}$", password)
        )

        if not username_valid:
            st.error("❌ Username must be Gmail or 10-digit phone number.")
        elif not password_valid:
            st.error("❌ Password must have 1 uppercase, 1 lowercase, 1 number, 1 special char, and be 8 chars.")
        else:
            st.session_state.form_data["username"] = username
            st.session_state.form_data["password"] = password
            next_page()

# ==================
# PAGE 2 – USER DETAILS
# ==================
elif st.session_state.page == 2:
    st.markdown("<h2>📝 User Details</h2>", unsafe_allow_html=True)

    name = st.text_input("Full Name", value=st.session_state.form_data.get("name", ""))
    gender = st.selectbox("Gender", ["male", "female"],
                          index=["male", "female"].index(st.session_state.form_data.get("gender", "male")))
    address = st.text_input("Address (max 20 chars)", max_chars=20,
                            value=st.session_state.form_data.get("address", ""))
    city = st.text_input("City", value=st.session_state.form_data.get("city", ""))
    state = st.text_input("State", value=st.session_state.form_data.get("state", ""))

    col1, col2 = st.columns(2)
    if col1.button("⬅ Back"):
        prev_page()
    if col2.button("Next ➡"):
        if not name.strip():
            st.error("❌ Please enter your name.")
        elif not address.strip():
            st.error("❌ Please enter your address.")
        elif not city.strip():
            st.error("❌ Please enter your city.")
        elif not state.strip():
            st.error("❌ Please enter your state.")
        else:
            st.session_state.form_data.update({
                "name": name,
                "gender": gender,
                "address": address,
                "city": city,
                "state": state
            })
            next_page()

# ==================
# PAGE 3 – MOBILE ADDICTION TRACKER
# ==================
elif st.session_state.page == 3:
    st.markdown("<h2>📱 Mobile Addiction Tracker</h2>", unsafe_allow_html=True)
    
    questions = {
        "gender": "Gender :",
        "feature1": "Do you use your phone to click pictures of class notes?",
        "feature2": "Do you buy books/access books from your mobile?",
        "feature3": "Does your phone's battery last a day?",
        "feature4": "When your phone's battery dies out, do you run for the charger?",
        "feature5": "Do you worry about losing your cell phone?",
        "feature6": "Do you take your phone to the bathroom?",
        "feature7": "Do you use your phone in any social gathering (parties)?",
        "feature8": "Do you often check your phone without any notification?",
        "feature9": "Do you check your phone just before going to sleep/just after waking up?",
        "feature10": "Do you keep your phone right next to you while sleeping?",
        "feature11": "Do you check emails, missed calls, texts during class time?",
        "feature12": "Do you find yourself relying on your phone when things get awkward?",
        "feature13": "Are you on your phone while watching TV or eating food?",
        "feature14": "Do you have a panic attack if you leave your phone elsewhere?",
        "feature15": "You don't mind responding to messages or checking your phone while on date?",
        "feature16": "For how long do you use your phone for playing games?",
        "feature17": "Can you live a day without phone?"
    }

    user_data = {}
    for feature, question in questions.items():
        prev_value = st.session_state.form_data.get(feature, "male" if feature == "gender" else "Yes")
        if feature == "gender":
            user_data[feature] = st.selectbox(f"👤 {question}", ["male", "female"], index=["male", "female"].index(prev_value))
        elif feature == "feature16":
            prev_value = st.session_state.form_data.get(feature, "<2 hours")
            user_data[feature] = st.selectbox(f"🎮 {question}", ["<2 hours", ">2 hours"], index=["<2 hours", ">2 hours"].index(prev_value))
        else:
            user_data[feature] = st.selectbox(f"📱 {question}", ["Yes", "No"], index=["Yes", "No"].index(prev_value))

    if st.button("🔍 Predict"):
        input_df = pd.DataFrame([user_data])
        input_df["gender"] = input_df["gender"].astype(str).str.lower()

        for col in input_df.columns:
            if col != "feature16" and col != "gender":
                input_df[col] = input_df[col].astype(str).str.capitalize()

        input_df["feature16"] = input_df["feature16"].replace({"<2 hours": 0, ">2 hours": 1}).astype(int)

        transformed_input = transformer.transform(input_df)
        pred_encoded = model.predict(transformed_input)[0]
        pred_label = label_encoder.inverse_transform([pred_encoded])[0]

        st.session_state.form_data.update(user_data)
        st.session_state.form_data["mobile_prediction"] = pred_label
        st.session_state.prediction_done = True

        if pred_label.lower() == "yes":
            st.markdown(
                """
                <div style="background-color:#ffe6e6; padding:15px; border-radius:10px; border:2px solid #ff4d4d;">
                    <h2 style="color:#ff1a1a; text-align:center;">🚨 Mobile Addiction Detected!</h2>
                    <p style="font-size:18px; text-align:center; color:#990000;">
                        Your answers indicate a high risk of mobile phone addiction. Please review the effects and solutions below.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")

            st.markdown(
                """
                ### 📉 **Physical Health Issues**
                - 👀 Eye strain, headaches, blurred vision  
                - 🪑 Poor posture → neck/back pain ("text neck")  
                - 🌙 Sleep disturbances from blue light exposure  
                - 😴 Fatigue from lack of rest & activity  
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                ### 🧠 **Mental Health Effects**
                - 😰 Increased stress, anxiety, irritability  
                - ⏳ Reduced attention span & concentration  
                - 😔 Higher risk of depression & isolation  
                - 📱 Dopamine dependency  
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                ### 🤝 **Social & Lifestyle Impacts**
                - 💔 Weakening real-life relationships  
                - 📉 Poor academic/work performance  
                - 🕒 Reduced productivity  
                - 🎯 Neglect of hobbies & fitness  
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                ### 💡 **Ways to Overcome**
                ✅ **Set limits** – Use digital wellbeing/screen time tools  
                ✅ **Change habits** – Keep phone away during meals/study  
                ✅ **Phone-free zones** – No phones in bedroom/social events  
                ✅ **Gradual reduction** – Take small breaks, increase over time  
                ✅ **Mindfulness** – Meditation & accountability with friends  
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")
            st.info("💬 Remember: Healthy mobile use = better focus, health, and relationships!")
        else:
            st.markdown(
                """
                <div style="background-color:#e6ffe6; padding:15px; border-radius:10px; border:2px solid #33cc33;">
                    <h2 style="color:#009900; text-align:center;">✅ Mobile Usage is Healthy!</h2>
                    <p style="font-size:18px; text-align:center; color:#006600;">
                        You are using your mobile wisely. Keep up your good habits! 📱💪
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅ Back", key="back_btn"):
            prev_page()
    with col2:
        if st.button("Next ➡", key="next_btn"):
            if not st.session_state.get("prediction_done", False):
                st.error("⚠ Please click 'Predict' before continuing.")
            else:
                next_page()

# ==================
# PAGE 4 – REVIEW & FEEDBACK
# ==================
elif st.session_state.page == 4:
    st.markdown("<h2>⭐ Review & Feedback</h2>", unsafe_allow_html=True)
    rating = st.slider("Rate us (1 to 5)", 1, 5)
    feedback = st.text_area("Your feedback (max 50 words)")

    if st.button("📤 Submit", use_container_width=True):
        if len(feedback.split()) > 50:
            st.error("❌ Feedback must be 50 words or less.")
        else:
            st.session_state.form_data.update({
                "rating": rating,
                "feedback": feedback
            })
            c.execute("""
                INSERT INTO user_info (
                    username, password, name, gender, address, city, state, 
                    mobile_prediction, rating, feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                st.session_state.form_data.get("username"),
                st.session_state.form_data.get("password"),
                st.session_state.form_data.get("name"),
                st.session_state.form_data.get("gender"),
                st.session_state.form_data.get("address"),
                st.session_state.form_data.get("city"),
                st.session_state.form_data.get("state"),
                st.session_state.form_data.get("mobile_prediction"),
                st.session_state.form_data.get("rating"),
                st.session_state.form_data.get("feedback")
            ))
            conn.commit()
            st.success("✅ Data submitted successfully!")
