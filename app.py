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
    max-width: 1150px;
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
.tag {
    display: inline-block;
    padding: 0.3rem 0.6rem;
    margin: 0.2rem 0.2rem 0 0;
    border-radius: 999px;
    border: 1px solid rgba(120,120,120,0.25);
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Nexus OS")
st.caption("Your personal AI orchestration layer")

GOAL_OPTIONS = [
    "Deep research only",
    "Research + blog / long-form",
    "Research + AI agent / prompt / config",
    "Research + slide deck / pitch",
    "Research + social media sequence",
    "Custom"
]

TOOL_OPTIONS = [
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

TOOL_ALIAS_MAP = {
    "perplexity": "Perplexity",
    "gemini": "Gemini",
    "claude": "Claude",
    "chatgpt": "ChatGPT",
    "chat gpt": "ChatGPT",
    "julius": "Julius AI",
    "julius ai": "Julius AI",
    "canva": "Canva",
    "gamma": "Gamma AI",
    "gamma ai": "Gamma AI",
    "aippt": "AIPPT",
    "notebooklm": "NotebookLM",
    "notebook lm": "NotebookLM",
    "grok": "Grok",
    "merlin": "Merlin"
}

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
if "recommended_stack" not in st.session_state:
    st.session_state.recommended_stack = []
if "alternative_stack" not in st.session_state:
    st.session_state.alternative_stack = []
if "recognized_tools" not in st.session_state:
    st.session_state.recognized_tools = []
if "unrecognized_tools" not in st.session_state:
    st.session_state.unrecognized_tools = []
if "task_input" not in st.session_state:
    st.session_state.task_input = ""

def get_tool_recommendations(goal):
    if goal == "Deep research only":
        return ["Perplexity", "NotebookLM"], ["Gemini", "Claude"]
    elif goal == "Research + blog / long-form":
        return ["Perplexity", "Gemini"], ["Claude", "ChatGPT"]
    elif goal == "Research + AI agent / prompt / config":
        return ["Perplexity", "Claude"], ["Gemini", "ChatGPT"]
    elif goal == "Research + slide deck / pitch":
        return ["Perplexity", "Gamma AI"], ["AIPPT", "Canva"]
    elif goal == "Research + social media sequence":
        return ["Perplexity", "Gemini"], ["ChatGPT", "Grok"]
    else:
        return ["Perplexity"], ["Gemini", "Claude", "ChatGPT"]

def swap_tool(old_tool, new_tool):
    updated = st.session_state.recommended_stack.copy()
    if old_tool in updated:
        idx = updated.index(old_tool)
        updated[idx] = new_tool
        st.session_state.recommended_stack = updated

def parse_tool_identifiers(raw_text):
    parts = [p.strip().lower() for p in raw_text.split(",") if p.strip()]
    recognized = []
    unrecognized = []

    for part in parts:
        if part in TOOL_ALIAS_MAP:
            mapped = TOOL_ALIAS_MAP[part]
            if mapped not in recognized:
                recognized.append(mapped)
        else:
            unrecognized.append(part)

    return recognized, unrecognized

with st.sidebar:
    st.header("System")
    st.write("Nexus OS v2")
    if st.button("Reset onboarding"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def onboarding():
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Layer 1 Onboarding")
    st.markdown('<div class="small-muted">Define the task and let Nexus OS recommend a best-fit tool stack.</div>', unsafe_allow_html=True)

    goal = st.selectbox("Select your primary goal:", GOAL_OPTIONS)

    output_format = st.selectbox(
        "Select your desired output format:",
        ["Text", "Markdown", "JSON", "Slide Outline", "Agent Prompt"]
    )

    optimization_pref = st.selectbox(
        "Select your optimization preference:",
        ["Accuracy", "Speed", "Cost", "Balanced"]
    )

    if st.button("Generate recommended stack", type="primary"):
        recommended, alternatives = get_tool_recommendations(goal)
        st.session_state.goal = goal
        st.session_state.output_format = output_format
        st.session_state.optimization_pref = optimization_pref
        st.session_state.recommended_stack = recommended
        st.session_state.alternative_stack = alternatives
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.onboarded and not st.session_state.recommended_stack:
    onboarding()
else:
    if not st.session_state.onboarded:
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.subheader("Recommended Stack")
        st.write(f"**Goal:** {st.session_state.goal}")
        st.write(f"**Output Format:** {st.session_state.output_format}")
        st.write(f"**Optimization Preference:** {st.session_state.optimization_pref}")

        st.markdown("**Primary recommendation**")
        for tool in st.session_state.recommended_stack:
            st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

        st.markdown("**One-click swaps**")
        if st.session_state.goal == "Research + blog / long-form":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Gemini → Claude"):
                    swap_tool("Gemini", "Claude")
                    st.rerun()
            with col2:
                if st.button("Swap Gemini → ChatGPT"):
                    swap_tool("Gemini", "ChatGPT")
                    st.rerun()

        elif st.session_state.goal == "Research + AI agent / prompt / config":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Claude → Gemini"):
                    swap_tool("Claude", "Gemini")
                    st.rerun()
            with col2:
                if st.button("Swap Claude → ChatGPT"):
                    swap_tool("Claude", "ChatGPT")
                    st.rerun()

        elif st.session_state.goal == "Research + slide deck / pitch":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Gamma AI → AIPPT"):
                    swap_tool("Gamma AI", "AIPPT")
                    st.rerun()
            with col2:
                if st.button("Swap Gamma AI → Canva"):
                    swap_tool("Gamma AI", "Canva")
                    st.rerun()

        elif st.session_state.goal == "Research + social media sequence":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Gemini → ChatGPT"):
                    swap_tool("Gemini", "ChatGPT")
                    st.rerun()
            with col2:
                if st.button("Swap Gemini → Grok"):
                    swap_tool("Gemini", "Grok")
                    st.rerun()

        st.markdown("**Alternatives**")
        for tool in st.session_state.alternative_stack:
            st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

        raw_tool_input = st.text_input(
            "Add tools by identifier or name (comma-separated)",
            placeholder="Example: perplexity, gamma, canva"
        )

        if st.button("Recognize typed tools"):
            recognized, unrecognized = parse_tool_identifiers(raw_tool_input)
            st.session_state.recognized_tools = recognized
            st.session_state.unrecognized_tools = unrecognized

        if st.session_state.recognized_tools:
            st.markdown("**Recognized tools**")
            for tool in st.session_state.recognized_tools:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

        if st.session_state.unrecognized_tools:
            st.markdown("**Unrecognized entries**")
            for tool in st.session_state.unrecognized_tools:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

        default_stack = list(dict.fromkeys(st.session_state.recommended_stack + st.session_state.recognized_tools))

        custom_stack = st.multiselect(
            "Customize your tool combo before continuing:",
            TOOL_OPTIONS,
            default=default_stack
        )

        if st.button("Confirm stack and continue", type="primary"):
            st.session_state.allowed_connectors = custom_stack
            st.session_state.onboarded = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        col1, col2 = st.columns([1.2, 1])

        with col1:
            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Workflow Summary")
            st.write(f"**Goal:** {st.session_state.goal}")
            st.write(f"**Output Format:** {st.session_state.output_format}")
            st.write(f"**Optimization Preference:** {st.session_state.optimization_pref}")
            st.write(f"**Selected Tool Stack:** {', '.join(st.session_state.allowed_connectors) if st.session_state.allowed_connectors else 'None selected'}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Execution Area")
            st.session_state.task_input = st.text_area(
                "Describe your task",
                value=st.session_state.task_input,
                placeholder="Example: Research AI adoption in India and create a detailed blog outline."
            )

            if st.button("Run workflow", type="primary"):
                st.info("Execution logic comes next. Dynamic connector recall is now live.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Suggested Alternatives")
            for tool in st.session_state.alternative_stack:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
