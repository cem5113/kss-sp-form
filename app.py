import streamlit as st
import pandas as pd
import time
import random
import datetime
from io import BytesIO
import os

SAVE_DIR = "."

st.set_page_config(page_title="Flight Fatigue Assessment", layout="centered")
st.title("🧠 Pilot Fatigue Assessment: KSS, SP & PVT")

st.markdown("""
This tool collects **subjective fatigue scores** and **reaction time** to monitor pilot fatigue before and after flights.
""")

# ✅ SESSION STATE INIT
for key, default in {
    "step": 0,
    "confirmed": False,
    "pvt_scores": [],
    "pvt_in_progress": False,
    "trial_start": None,
    "reactions": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# STEP 1: Fatigue Form
if st.session_state.step == 0:
    st.subheader("👤 Pilot Information")
    pilot_id = st.text_input("Pilot ID")
    flight_type = st.selectbox("Flight Type", ["Ab Initio", "First Officer", "Operational Pilot"])
    flight_phase = st.radio("Flight Phase", ["Pre-Flight", "Post-Flight"])
    flight_date = st.date_input("Date", datetime.date.today())

    st.subheader("😴 Karolinska Sleepiness Scale (KSS)")
    st.markdown("- 1 = Extremely alert\n- 3 = Alert\n- 5 = Neither alert nor sleepy\n- 7 = Sleepy, but no effort to stay awake\n- 9 = Very sleepy, fighting sleep")
    kss = st.slider("Select KSS Score", 1, 9, 5)

    st.subheader("😩 Samn–Perelli Fatigue Scale (SP)")
    st.markdown("- 1 = Fully alert\n- 3 = Somewhat tired\n- 5 = Very tired\n- 7 = Completely exhausted")
    sp = st.slider("Select SP Score", 1, 7, 3)

    if st.button("Review and Confirm"):
        st.session_state.form_data = {
            "Pilot_ID": pilot_id,
            "Flight_Type": flight_type,
            "Flight_Phase": flight_phase,
            "Date": flight_date,
            "KSS": kss,
            "SP": sp
        }
        st.session_state.step = 1

# STEP 2: Confirm Inputs
elif st.session_state.step == 1:
    st.subheader("📋 Confirm Your Inputs")
    st.write(pd.DataFrame([st.session_state.form_data]))

    if st.button("✅ Confirm and Proceed to PVT"):
        st.session_state.confirmed = True
        st.session_state.step = 2
    elif st.button("🔄 Edit Inputs"):
        st.session_state.step = 0

# STEP 3: PVT Test (2 attempts max)
elif st.session_state.step == 2:
    st.subheader("🎮 PVT (Psychomotor Vigilance Task) Test")

    st.markdown("""
    - You can perform the PVT test **up to two times**.
    - Your **best (lowest) average reaction time** will be saved.
    - After your first attempt, you can either accept the result or try again.
    """)

    if not st.session_state.pvt_in_progress and len(st.session_state.pvt_scores) < 2:
        if st.button("▶️ Start PVT Test"):
            st.session_state.pvt_in_progress = True
            st.session_state.trial_start = time.time() + random.uniform(2, 5)
            st.session_state.reactions = []

    # PVT Logic
    if st.session_state.pvt_in_progress:
        now = time.time()
        wait_time = st.session_state.trial_start - now

        if wait_time > 0:
            with st.empty():
                while time.time() < st.session_state.trial_start:
                    remaining = int(st.session_state.trial_start - time.time()) + 1
                    st.info(f"⏳ Wait for green signal... ({remaining} sec)")
                    time.sleep(1)
            st.experimental_rerun()
        else:
            st.success("🟢 CLICK NOW!")
            if st.button("Click!"):
                reaction = (time.time() - st.session_state.trial_start) * 1000
                st.session_state.reactions.append(reaction)
                avg_rt = sum(st.session_state.reactions) / len(st.session_state.reactions)
                st.success(f"Your reaction time: {reaction:.1f} ms (Avg: {avg_rt:.1f} ms)")
                st.session_state.pvt_scores.append(avg_rt)
                st.session_state.pvt_in_progress = False
                st.session_state.trial_start = None

    if st.session_state.pvt_scores:
        st.subheader("📊 PVT Attempt Results")
        for i, score in enumerate(st.session_state.pvt_scores):
            st.write(f"Attempt {i+1}: Avg Reaction Time = {score:.1f} ms")

        if len(st.session_state.pvt_scores) == 1:
            if st.button("🔁 Try Again (Final Attempt)"):
                st.session_state.pvt_in_progress = False
                st.session_state.trial_start = None
                st.session_state.reactions = []

        if st.button("💾 Save and Finish"):
            st.session_state.step = 3

# STEP 4: Save Result
elif st.session_state.step == 3:
    best_pvt = min(st.session_state.pvt_scores)
    result = st.session_state.form_data.copy()
    result["Best_PVT_ms"] = round(best_pvt, 2)

    st.success("✅ Final Result")
    df = pd.DataFrame([result])
    st.dataframe(df)

    # Save to Excel
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{result['Pilot_ID']}_{result['Flight_Phase']}_{timestamp}.xlsx"
    save_path = os.path.join(SAVE_DIR, filename)

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Fatigue_Result')
    output.seek(0)

    with open(save_path, "wb") as f:
        f.write(output.getvalue())

    st.success(f"✅ Excel file saved to: `{save_path}`")
    st.download_button("📥 Download Excel File", data=output.getvalue(), file_name=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
