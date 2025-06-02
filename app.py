import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials

# === Function: Append to Google Sheets ===
def append_to_google_sheet(data_row):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(st.secrets["google_sheets"], scopes=scope)
    client = gspread.authorize(creds)

    try:
        sheet = client.open("Pilot_Fatigue_Records").worksheet("FormData")
    except Exception as e:
        st.error(f"❌ Google Sheet veya 'FormData' sekmesi bulunamadı: {e}")
        return

    # Avoid duplicate submissions
    try:
        existing_records = sheet.get_all_records()
        for row in existing_records:
            if (
                row.get("Pilot_ID") == data_row[0]
                and row.get("Flight_Phase") == data_row[2]
                and row.get("Date") == data_row[3]
            ):
                raise Exception("Duplicate submission detected.")
    except Exception as e:
        st.warning(f"⚠️ Duplicate kontrolünde hata: {e}")
        return

    try:
        sheet.append_row(data_row)
        st.success("✅ Data has been successfully submitted to Google Sheets.")
    except Exception as e:
        st.error(f"❌ Submission failed: {e}")

# === Streamlit App UI ===
st.set_page_config(page_title="KSS & SP Fatigue Assessment", layout="centered")
st.title("🧑‍✈️ Pilot Fatigue Self-Assessment Form")

st.markdown("""
This form allows helicopter pilots to self-report their fatigue levels **before and after flights** using:

- **KSS (Karolinska Sleepiness Scale)**  
- **SP (Samn–Perelli Fatigue Scale)**  
You will first review and confirm your responses before sending.
""")

if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

with st.form("fatigue_form"):
    st.subheader("✈️ Pilot Information")
    pilot_id = st.text_input("Pilot ID", placeholder="e.g., User001")
    flight_type = st.selectbox("Flight Type", ["Ab Initio", "First Officer", "Operational Pilot"])
    flight_phase = st.radio("Assessment Time", ["Pre-Flight", "Post-Flight"])
    date = st.date_input("Date", datetime.date.today())
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    st.subheader("😫 Karolinska Sleepiness Scale (KSS)")
    kss = st.slider("Select your KSS score", 1, 9, 5)

    st.subheader("😩 Samn–Perelli Fatigue Scale (SP)")
    sp = st.slider("Select your SP score", 1, 7, 3)

    review = st.form_submit_button("Review Your Submission")

# === Step 2: Review and Confirm ===
if review and not st.session_state.confirmed:
    st.write("📋 Please review your responses below:")
    st.dataframe(pd.DataFrame([{
        "Pilot_ID": pilot_id,
        "Flight_Type": flight_type,
        "Flight_Phase": flight_phase,
        "Date": date,
        "Time_Submitted": timestamp,
        "KSS": kss,
        "SP": sp
    }]))

    if st.button("✅ Confirm and Send to Operator"):
        append_to_google_sheet([
            pilot_id,
            flight_type,
            flight_phase,
            str(date),
            timestamp,
            kss,
            sp
        ])
        st.session_state.confirmed = True

# === Already submitted
if st.session_state.confirmed:
    st.info("✅ You have already submitted your data. To make corrections, please contact the operator.")
