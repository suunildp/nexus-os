import streamlit as st

st.set_page_config(
    page_title="Nexus OS",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 Nexus OS")
st.caption("Personal AI orchestration layer")

if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if "goal" not in st.session_state:
    st.session_state.goal = ""

if "output_format" not in st.session_state:
    st.session_state.output_format = "Text"

if "optimization_pref" not in st.session_state:
    st.session_state.optimization_pref = "Accuracy"

if "allowed_connectors" not in st.session_state:
    st.session_state.allowed_connectors = []

def onboarding():
    st.subheader("Layer 1 Onboarding")

    goal = st.text_input("What is your goal for using Nexus OS?")
    output_format = st.selectbox(
        "Select your desired output format:",
        ["Text", "Markdown", "JSON"]
    )
    optimization_pref = st.selectbox(
        "Select your optimization preference:",
        ["Accuracy", "Speed", "Cost"]
    )
    allowed_connectors = st.multiselect(
        "Select allowed connectors:",
        [
            "Perplexity",
            "Gemini",
            "Claude",
            "ChatGPT",
            "Julius AI",
            "Canva",
            "Gamma AI",
            "AIPPT",
            "NotebookLM",
            "Grok",
            "Merlin"
        ]
    )

    if st.button("Confirm onboarding", type="primary"):
        st.session_state.goal = goal
        st.session_state.output_format = output_format
        st.session_state.optimization_pref = optimization_pref
        st.session_state.allowed_connectors = allowed_connectors
        st.session_state.onboarded = True
        st.rerun()

if not st.session_state.onboarded:
    onboarding()
else:
    st.success("Onboarding completed.")
    st.write(f"**Goal:** {st.session_state.goal}")
    st.write(f"**Output Format:** {st.session_state.output_format}")
    st.write(f"**Optimization Preference:** {st.session_state.optimization_pref}")
    st.write(f"**Allowed Connectors:** {', '.join(st.session_state.allowed_connectors) if st.session_state.allowed_connectors else 'None selected'}")

    st.divider()
    st.subheader("Execution Area")
    user_prompt = st.text_area("Describe your task")
    if st.button("Run workflow"):
        st.info("v2 starter is live. Next we will wire orchestration, one-click swaps, and authentication.")
