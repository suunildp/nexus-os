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
.section-label {
    margin-top: 1rem;
    margin-bottom: 0.35rem;
    font-weight: 600;
}
.status-ok {
    color: #4ade80;
    font-weight: 600;
}
.status-pending {
    color: #fbbf24;
    font-weight: 600;
}
.connector-row {
    padding: 0.6rem 0;
    border-bottom: 1px solid rgba(120,120,120,0.15);
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

CONNECTOR_REGISTRY = {
    "Perplexity": {"auth_type": "API Key", "connected": False},
    "Gemini": {"auth_type": "API Key", "connected": False},
    "Claude": {"auth_type": "API Key", "connected": False},
    "ChatGPT": {"auth_type": "API Key", "connected": False},
    "Julius AI": {"auth_type": "API Key", "connected": False},
    "Canva": {"auth_type": "OAuth / API", "connected": False},
    "Gamma AI": {"auth_type": "OAuth / API", "connected": False},
    "AIPPT": {"auth_type": "OAuth / API", "connected": False},
    "NotebookLM": {"auth_type": "OAuth / API", "connected": False},
    "Grok": {"auth_type": "API Key", "connected": False},
    "Merlin": {"auth_type": "API Key", "connected": False}
}

if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "goal" not in st.session_state:
    st.session_state.goal = ""
if "output_format" not in st.session_state:
    st.session_state.output_format = "Text"
if "optimization_pref" not in st.session_state:
    st.session_state.optimization_pref = "Accuracy"
if "selected_stack" not in st.session_state:
    st.session_state.selected_stack = []
if "suggested_stack" not in st.session_state:
    st.session_state.suggested_stack = []
if "alternative_stack" not in st.session_state:
    st.session_state.alternative_stack = []
if "recognized_tools" not in st.session_state:
    st.session_state.recognized_tools = []
if "unrecognized_tools" not in st.session_state:
    st.session_state.unrecognized_tools = []
if "task_input" not in st.session_state:
    st.session_state.task_input = ""
if "connector_registry" not in st.session_state:
    st.session_state.connector_registry = CONNECTOR_REGISTRY.copy()

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
    updated = st.session_state.suggested_stack.copy()
    if old_tool in updated:
        idx = updated.index(old_tool)
        updated[idx] = new_tool
        st.session_state.suggested_stack = updated

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

def connect_tool(tool_name):
    st.session_state.connector_registry[tool_name]["connected"] = True

with st.sidebar:
    st.header("System")
    st.write("Nexus OS v2")
    if st.button("Reset onboarding"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("### Connector Status")
    if st.session_state.selected_stack:
        for tool in st.session_state.selected_stack:
            if st.session_state.connector_registry[tool]["connected"]:
                st.markdown(f"**{tool}** — <span class='status-ok'>Connected</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"**{tool}** — <span class='status-pending'>Not connected</span>", unsafe_allow_html=True)
    else:
        st.caption("No tools selected yet.")

def onboarding():
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Layer 1 Onboarding")
    st.markdown('<div class="small-muted">Define the task and let Nexus OS suggest a best-fit tool stack.</div>', unsafe_allow_html=True)

    goal = st.selectbox("Select your primary goal:", GOAL_OPTIONS)

    output_format = st.selectbox(
        "Select your desired output format:",
        ["Text", "Markdown", "JSON", "Slide Outline", "Agent Prompt"]
    )

    optimization_pref = st.selectbox(
        "Select your optimization preference:",
        ["Accuracy", "Speed", "Cost", "Balanced"]
    )

    if st.button("Generate suggested stack", type="primary"):
        suggested, alternatives = get_tool_recommendations(goal)
        st.session_state.goal = goal
        st.session_state.output_format = output_format
        st.session_state.optimization_pref = optimization_pref
        st.session_state.suggested_stack = suggested
        st.session_state.selected_stack = suggested.copy()
        st.session_state.alternative_stack = alternatives
        st.session_state.recognized_tools = []
        st.session_state.unrecognized_tools = []
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.onboarded and not st.session_state.suggested_stack:
    onboarding()
else:
    if not st.session_state.onboarded:
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.subheader("Tool Planning")
        st.write(f"**Goal:** {st.session_state.goal}")
        st.write(f"**Output Format:** {st.session_state.output_format}")
        st.write(f"**Optimization Preference:** {st.session_state.optimization_pref}")

        st.markdown('<div class="section-label">Suggested stack</div>', unsafe_allow_html=True)
        for tool in st.session_state.suggested_stack:
            st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">One-click swaps</div>', unsafe_allow_html=True)
        if st.session_state.goal == "Research + blog / long-form":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Gemini → Claude"):
                    swap_tool("Gemini", "Claude")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()
            with col2:
                if st.button("Swap Gemini → ChatGPT"):
                    swap_tool("Gemini", "ChatGPT")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()

        elif st.session_state.goal == "Research + AI agent / prompt / config":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Claude → Gemini"):
                    swap_tool("Claude", "Gemini")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()
            with col2:
                if st.button("Swap Claude → ChatGPT"):
                    swap_tool("Claude", "ChatGPT")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()

        elif st.session_state.goal == "Research + slide deck / pitch":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Gamma AI → AIPPT"):
                    swap_tool("Gamma AI", "AIPPT")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()
            with col2:
                if st.button("Swap Gamma AI → Canva"):
                    swap_tool("Gamma AI", "Canva")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()

        elif st.session_state.goal == "Research + social media sequence":
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Swap Gemini → ChatGPT"):
                    swap_tool("Gemini", "ChatGPT")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()
            with col2:
                if st.button("Swap Gemini → Grok"):
                    swap_tool("Gemini", "Grok")
                    st.session_state.selected_stack = st.session_state.suggested_stack.copy()
                    st.rerun()

        st.markdown('<div class="section-label">Alternatives</div>', unsafe_allow_html=True)
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
            merged = list(dict.fromkeys(st.session_state.suggested_stack + recognized))
            st.session_state.selected_stack = merged

        if st.session_state.recognized_tools:
            st.markdown('<div class="section-label">Recognized from your input</div>', unsafe_allow_html=True)
            for tool in st.session_state.recognized_tools:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

        if st.session_state.unrecognized_tools:
            st.markdown('<div class="section-label">Unrecognized entries</div>', unsafe_allow_html=True)
            for tool in st.session_state.unrecognized_tools:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Your selected stack</div>', unsafe_allow_html=True)
        selected_stack = st.multiselect(
            "Review or customize your final tool combo:",
            TOOL_OPTIONS,
            default=st.session_state.selected_stack
        )
        st.session_state.selected_stack = selected_stack

        st.markdown('<div class="section-label">Connection readiness</div>', unsafe_allow_html=True)
        for tool in st.session_state.selected_stack:
            st.markdown(f"<div class='connector-row'><b>{tool}</b> — {st.session_state.connector_registry[tool]['auth_type']}</div>", unsafe_allow_html=True)

        if st.button("Confirm stack and continue", type="primary"):
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
            st.write(f"**Selected Tool Stack:** {', '.join(st.session_state.selected_stack) if st.session_state.selected_stack else 'None selected'}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Connector Registry")
            for tool in st.session_state.selected_stack:
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    status = "Connected" if st.session_state.connector_registry[tool]["connected"] else "Not connected"
                    auth_type = st.session_state.connector_registry[tool]["auth_type"]
                    st.write(f"**{tool}** — {auth_type} — {status}")
                with col_b:
                    if not st.session_state.connector_registry[tool]["connected"]:
                        if st.button(f"Connect {tool}", key=f"connect_{tool}"):
                            connect_tool(tool)
                            st.rerun()
                    else:
                        st.success("Ready")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Execution Area")
            st.session_state.task_input = st.text_area(
                "Describe your task",
                value=st.session_state.task_input,
                placeholder="Example: Research AI adoption in India and create a detailed blog outline."
            )

            if st.button("Run workflow", type="primary"):
                unconnected = [
                    tool for tool in st.session_state.selected_stack
                    if not st.session_state.connector_registry[tool]["connected"]
                ]
                if unconnected:
                    st.warning(f"Please connect these tools first: {', '.join(unconnected)}")
                else:
                    st.success("All selected connectors are marked connected. Real execution wiring comes next.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Plan Snapshot")
            st.write("**Suggested stack:**")
            for tool in st.session_state.suggested_stack:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

            st.write("**Selected stack:**")
            for tool in st.session_state.selected_stack:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
