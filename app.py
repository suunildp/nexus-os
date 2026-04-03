import streamlit as st

st.set_page_config(
    page_title="Nexus OS",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1100px;
}
.nexus-card {
    padding: 1rem 1.25rem;
    border: 1px solid rgba(120,120,120,0.2);
    border-radius: 14px;
    margin-bottom: 1rem;
    background: rgba(255,255,255,0.03);
}
.small-muted {
    color: #888;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Nexus OS")
st.caption("Your personal AI orchestration layer")

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

if "task_input" not in st.session_state:
    st.session_state.task_input = ""

with st.sidebar:
    st.header("System")
    st.write("Nexus OS v2 starter")
    if st.button("Reset onboarding"):
        st.session_state.onboarded = False
        st.session_state.goal = ""
        st.session_state.output_format = "Text"
        st.session_state.optimization_pref = "Accuracy"
        st.session_state.allowed_connectors = []
        st.session_state.task_input = ""
        st.rerun()

def onboarding():
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Layer 1 Onboarding")
    st.markdown('<div class="small-muted">Define the task before orchestration begins.</div>', unsafe_allow_html=True)

    goal = st.text_input(
        "What is your goal for using Nexus OS?",
        placeholder="Example: Research + blog on AI adoption in Indian enterprises"
    )

    output_format = st.selectbox(
        "Select your desired output format:",
        ["Text", "Markdown", "JSON", "Slide Outline", "Agent Prompt"]
    )

    optimization_pref = st.selectbox(
        "Select your optimization preference:",
        ["Accuracy", "Speed", "Cost", "Balanced"]
    )

    allowed_connectors = st.multiselect(
        "Select allowed connectors/tools:",
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

    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.onboarded:
    onboarding()
else:
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.subheader("Workflow Summary")
        st.write(f"**Goal:** {st.session_state.goal}")
        st.write(f"**Output Format:** {st.session_state.output_format}")
        st.write(f"**Optimization Preference:** {st.session_state.optimization_pref}")
        st.write(f"**Allowed Connectors:** {', '.join(st.session_state.allowed_connectors) if st.session_state.allowed_connectors else 'None selected'}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.subheader("Execution Area")
        st.session_state.task_input = st.text_area(
            "Describe your task",
            value=st.session_state.task_input,
            placeholder="Example: Create a cited blog outline and recommend the best tool chain."
        )

        if st.button("Run workflow", type="primary"):
            st.info("Execution logic comes next. v2 is live and ready for orchestration wiring.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.subheader("Recommended Next Step")
        st.write("Next, we will add:")
        st.write("- dynamic connector selection")
        st.write("- one-click swaps for alternatives")
        st.write("- tool recommendation logic")
        st.write("- authentication flow")
        st.markdown('</div>', unsafe_allow_html=True)
