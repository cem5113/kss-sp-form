# app.py

import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

st.set_page_config(page_title="KSS & SP Fatigue Assessment", layout="centered")
st.title("🧠 KSS & SP Fatigue Assessment Form")

st.markdown("This form allows helicopter pilots to self-report their fatigue levels **before and after flights** using the Karolinska Sleepiness Scale (KSS) and Samn–Perelli Fatigue Scale (SP).")

with st.form("fatigue_form"):
    st.subheader("✈️ Pilot Information")
    pilot_id = st.text_input("Pilot ID or Code")
    flight_type = st.selectbox("Flight Type", ["Instructor", "First Officer", "Pilot"])
    flight_phase = st.radio("Assessment Time", ["Pre-Flight", "Post-Flight"])
    date = st.date_input("Date", datetime.date.today())

    st.subheader("😴 KSS (Karolinska Sleepiness Scale)")
    kss = st.slider("KSS Score (1 = Very alert, 9 = Fighting sleep)", 1, 9, 5)

    st.subheader("😩 SP (Samn–Perelli Fatigue Scale)")
    sp = st.slider("SP Score (1 = Fully alert, 7 = Completely exhausted)", 1, 7, 3)

    submitted = st.form_submit_button("Submit")

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
        writer.save()
    output.seek(0)

    st.success("✅ Your data has been recorded below:")
    st.dataframe(df)

    st.download_button(
        label="📥 Download as Excel",
        data=output,
        file_name="kss_sp_submission.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
