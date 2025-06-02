# app.py

import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

st.set_page_config(page_title="KSS & SP Fatigue Assessment", layout="centered")
st.title("🧠 KSS & SP Fatigue Assessment Form")

st.markdown("""
This form allows helicopter pilots to self-report their fatigue levels **before and after flights** using:

- **KSS (Karolinska Sleepiness Scale)**
- **SP (Samn–Perelli Fatigue Scale)**
""")

with st.form("fatigue_form"):
    st.subheader("✈️ Pilot Information")
    pilot_id = st.text_input("Pilot ID or Code")
    flight_type = st.selectbox("Flight Type", ["Instructor", "First Officer", "Pilot"])
    flight_phase = st.radio("Assessment Time", ["Pre-Flight", "Post-Flight"])
    date = st.date_input("Date", datetime.date.today())

    st.subheader("😴 KSS - Karolinska Sleepiness Scale")
    st.markdown("""
**The Karolinska Sleepiness Scale (KSS)** is a self-rated scale that reflects your current level of sleepiness:

- 1 = Extremely alert  
- 3 = Alert  
- 5 = Neither alert nor sleepy  
- 7 = Sleepy, but no effort to stay awake  
- 9 = Very sleepy, fighting sleep
""")
    kss = st.slider("Select your KSS score", 1, 9, 5)

    st.subheader("😩 SP - Samn–Perelli Fatigue Scale")
    st.markdown("""
**The Samn–Perelli Fatigue Scale (SP)** is used to rate general fatigue level during operational tasks:

- 1 = Fully alert  
- 3 = Somewhat tired  
- 5 = Very tired  
- 7 = Completely exhausted
""")
    sp = st.slider("Select your SP score", 1, 7, 3)

    submitted = st.form_submit_button("Submit")

    st.markdown("""
    📌 *Please make sure to inform the operator after completing the form to ensure your data is properly collected.*
    """)

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
        df.to_excel(writer, index=False, sheet_name='KSS_SP_Data')

    output.seek(0)

    st.success("✅ Your data has been recorded below:")
    st.dataframe(df)

    st.download_button(
        label="📥 Download as Excel",
        data=output,
        file_name="kss_sp_submission.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ) 
