import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === Function: Append to Google Sheets ===
def append_to_google_sheet(data_row):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Pilot_Fatigue_Records").worksheet("FormData")
    sheet.append_row(data_row)

# === Streamlit App UI ===
st.set_page_config(page_title="KSS & SP Fatigue Assessment", layout="centered")
st.title("🧠 Pilot Fatigue Self-Assessment Form")

st.markdown("""
This form allows helicopter pilots to self-report their fatigue levels **before and after flights** using:

- **KSS (Karolinska Sleepiness Scale)**
- **SP (Samn–Perelli Fatigue Scale)**

After submission, your data will be automatically saved to the operator's database.
""")

with st.form("fatigue_form"):
    st.subheader("✈️ Pilot Information")
    pilot_id = st.text_input("Pilot ID")
    flight_type = st.selectbox("Flight Type", ["Ab Initio", "First Officer", "Operational Pilot"])
    flight_phase = st.radio("Assessment Time", ["Pre-Flight", "Post-Flight"])
    date = st.date_input("Date", datetime.date.today())

    st.subheader("😴 Karolinska Sleepiness Scale (KSS)")
    st.markdown("""
**KSS** reflects your current level of sleepiness:

- 1 = Extremely alert  
- 3 = Alert  
- 5 = Neither alert nor sleepy  
- 7 = Sleepy, but no effort to stay awake  
- 9 = Very sleepy, fighting sleep
""")
    kss = st.slider("Select your KSS score", 1, 9, 5)

    st.subheader("😩 Samn–Perelli Fatigue Scale (SP)")
    st.markdown("""
**SP** reflects your overall fatigue level during operational tasks:

- 1 = Fully alert  
- 3 = Somewhat tired  
- 5 = Very tired  
- 7 = Completely exhausted
""")
    sp = st.slider("Select your SP score", 1, 7, 3)

    submitted = st.form_submit_button("Submit")

# === Submission Result ===
if submitted:
    new_row = {
        "Pilot_ID": pilot_id,
        "Flight_Type": flight_type,
        "Flight_Phase": flight_phase,
        "Date": date,
        "KSS": kss,
        "SP": sp
    }

    df = pd.DataFrame([new_row])
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fatigue_Form')
    output.seek(0)

    # 🔁 Send to Google Sheets
    try:
        append_to_google_sheet([
            pilot_id,
            flight_type,
            flight_phase,
            str(date),
            kss,
            sp
        ])
        st.success("✅ Your data has been successfully submitted to the operator.")
    except Exception as e:
        st.error(f"❌ Failed to send data to Google Sheets: {e}")

    # 📋 Show + Download
    st.success("📋 Your submission:")
    st.dataframe(df)

    st.download_button(
        label="📥 Download Excel File",
        data=output,
        file_name="kss_sp_submission.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
