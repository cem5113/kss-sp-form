import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import hashlib
import streamlit.components.v1 as components

# === PAGE CONFIG ===
st.set_page_config(page_title="Pilot Fatigue Assessment", layout="centered")
st.title("🧠 Pilot Fatigue Assessment: KSS, SP & PVT")

# === SESSION STATE INIT ===
for key in ["step", "kss", "sp", "pvt_results", "attempt", "authenticated"]:
    if key not in st.session_state:
        st.session_state[key] = 0 if key == "step" else [] if key == "pvt_results" else 0 if key == "attempt" else False

# === HASHED PASSWORD VALIDATION ===
def check_password(pilot_id, password):
    correct_hash = hashlib.sha256("1234".encode()).hexdigest()
    return hashlib.sha256(password.encode()).hexdigest() == correct_hash

# === LOGIN STEP ===
if not st.session_state.authenticated:
    st.subheader("🔐 Pilot Login")
    pilot_id = st.text_input("Pilot ID", max_chars=20)
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_password(pilot_id, password):
            st.session_state.authenticated = True
            st.session_state.pilot_id = pilot_id
            st.success("Login successful!")
        else:
            st.error("Invalid ID or password.")
    st.stop()

# === STEP 1: KSS & SP FORM ===
if st.session_state.step == 0:
    st.subheader("📝 Fatigue Self-Assessment")
    st.markdown("""
    ### 🧾 About the Scales
    
    - **Karolinska Sleepiness Scale (KSS):** Rates how sleepy you feel right now, from 1 (Very alert) to 9 (Very sleepy).
    - **Samn–Perelli Scale (SP):** Measures fatigue level, from 1 (Fully alert) to 7 (Completely exhausted).
    """)
    st.session_state.kss = st.slider("Karolinska Sleepiness Scale (1=Very alert, 9=Very sleepy)", 1, 9, 5)
    st.session_state.sp = st.slider("Samn–Perelli Fatigue Scale (1=Fully alert, 7=Completely exhausted)", 1, 7, 4)
    if st.button("Continue to Reaction Test"):
        st.session_state.step = 1
        st.rerun()

# === STEP 2: INLINE PVT TEST ===
if st.session_state.step == 1:
    st.subheader("🧪 Psychomotor Vigilance Test")
    st.info("You will be shown a red circle. Click it as fast as you can when it appears.")
    st.markdown("""
    <iframe src="https://pvt-test.streamlit.app" width="100%" height="500"></iframe>
    """, unsafe_allow_html=True)
    st.warning("Once your PVT test ends, please enter your average reaction time and number of lapses.")

    avg_rt = st.number_input("Average Reaction Time (ms)", min_value=0, step=1)
    lapses = st.number_input("Lapses (RT > 500 ms)", min_value=0, step=1)

    if st.button("Submit All Results"):
        st.session_state.pvt_results = {
            "avg_rt": avg_rt,
            "lapses": lapses
        }
        st.session_state.step = 2
        st.rerun()

# === STEP 3: WRITE TO GOOGLE SHEETS ===
if st.session_state.step == 2:
    st.subheader("📤 Submitting Data...")

    # Google Sheets API Setup
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_sheets"], scope)
    client = gspread.authorize(creds)
    sheet = client.open("Pilot_Fatigue_Results")

    sheet_name = f"pilot_{st.session_state.pilot_id}"
    try:
        worksheet = sheet.worksheet(sheet_name)
    except:
        worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="20")
        worksheet.append_row(["Timestamp", "KSS", "SP", "Avg_RT (ms)", "Lapses"])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = [now, st.session_state.kss, st.session_state.sp, st.session_state.pvt_results["avg_rt"], st.session_state.pvt_results["lapses"]]
    worksheet.append_row(new_row)

    st.success("✅ Results submitted successfully!")
    st.session_state.step = 3
    st.rerun()

# === STEP 4: DISPLAY PAST RECORDS ===
if st.session_state.step == 3:
    st.subheader("📈 Your Previous Results")
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["google_sheets"], scope)
    client = gspread.authorize(creds)
    sheet = client.open("Pilot_Fatigue_Results")
    worksheet = sheet.worksheet(f"pilot_{st.session_state.pilot_id}")
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    st.dataframe(df)

    st.info("You may close the app now. Thank you for your input.")
