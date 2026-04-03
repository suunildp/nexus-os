import os
import re
import requests
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

for key, value in {
    "onboarded": False,
    "goal": "",
    "output_format": "Text",
    "optimization_pref": "Accuracy",
    "selected_stack": [],
    "suggested_stack": [],
    "alternative_stack": [],
    "recognized_tools": [],
    "unrecognized_tools": [],
    "task_input": "",
    "connector_registry": CONNECTOR_REGISTRY.copy(),
    "perplexity_key_session": "",
    "perplexity_result": "",
    "perplexity_citations": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

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
    cleaned = raw_text.strip().lower()
    if not cleaned:
        return [], []
    if len(cleaned) > 200:
        return [], ["input too long"]
    if not re.fullmatch(r"[a-z0-9,\-\s]+", cleaned):
        return [], ["invalid characters in tool input"]

    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
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

def get_perplexity_api_key():
    env_key = os.environ.get("PERPLEXITY_API_KEY", "").strip()
    if env_key:
        return env_key, "railway"
    session_key = st.session_state.perplexity_key_session.strip()
    if session_key:
        return session_key, "session"
    return "", ""

def validate_perplexity_key(key):
    return key.startswith("pplx_") or key.startswith("pxl_") or len(key) > 20

def connect_perplexity():
    key, source = get_perplexity_api_key()
    if not key:
        return False, "No Perplexity API key found. Add it in Railway Variables or enter it in the masked field."
    if not validate_perplexity_key(key):
        return False, "Perplexity API key format looks invalid."
    st.session_state.connector_registry["Perplexity"]["connected"] = True
    return True, f"Perplexity connected via {source} key."

def run_perplexity_research(user_prompt):
    key, _ = get_perplexity_api_key()
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": "You are a precise research assistant. Give a concise, well-structured answer."
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }
    response = requests.post(
        "https://api.perplexity.ai/v1/sonar",
        headers=headers,
        json=payload,
        timeout=45
    )
    response.raise_for_status()
    data = response.json()
    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    citations = data.get("citations", [])
    return content, citations

with st.sidebar:
    st.header("System")
    st.write("Nexus OS v2")

    if st.button("Reset onboarding"):
        keys_to_keep = []
        for k in list(st.session_state.keys()):
            if k not in keys_to_keep:
                del st.session_state[k]
        st.rerun()

    st.markdown("### Perplexity Connection")

    env_key_present = bool(os.environ.get("PERPLEXITY_API_KEY", "").strip())
    if env_key_present:
        st.success("Railway environment key detected for Perplexity.")
    else:
        st.info("No Railway environment key detected. You can use the temporary masked field below.")

    temp_key = st.text_input(
        "Temporary Perplexity API key",
        value=st.session_state.perplexity_key_session,
        type="password",
        help="For testing only. Production is safer with Railway Variables."
    )
    st.session_state.perplexity_key_session = temp_key

    if st.button("Connect Perplexity"):
        ok, message = connect_perplexity()
        if ok:
            st.success(message)
        else:
            st.error(message)

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
            auth_type = st.session_state.connector_registry[tool]["auth_type"]
            st.markdown(f"<div class='connector-row'><b>{tool}</b> — {auth_type}</div>", unsafe_allow_html=True)

        if st.button("Confirm stack and continue", type="primary"):
            st.session_state.onboarded = True
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    else:
        col1, col2 = st.columns([1.25, 1])

        with col1:
            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Workflow Summary")
            st.write(f"**Goal:** {st.session_state.goal}")
            st.write(f"**Output Format:** {st.session_state.output_format}")
            st.write(f"**Optimization Preference:** {st.session_state.optimization_pref}")
            st.write(f"**Selected Tool Stack:** {', '.join(st.session_state.selected_stack) if st.session_state.selected_stack else 'None selected'}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Execution Area")
            st.session_state.task_input = st.text_area(
                "Describe your task",
                value=st.session_state.task_input,
                placeholder="Example: Research AI adoption in India and create a detailed blog outline.",
                max_chars=3000
            )

            if st.button("Run workflow", type="primary"):
                if "Perplexity" not in st.session_state.selected_stack:
                    st.error("Perplexity must be included in the selected stack for this version.")
                elif not st.session_state.connector_registry["Perplexity"]["connected"]:
                    st.error("Please connect Perplexity first.")
                elif not st.session_state.task_input.strip():
                    st.error("Please enter a task.")
                else:
                    try:
                        result, citations = run_perplexity_research(st.session_state.task_input.strip())
                        st.session_state.perplexity_result = result
                        st.session_state.perplexity_citations = citations
                        st.success("Perplexity research completed.")
                    except requests.HTTPError:
                        st.error("Perplexity API request failed. Check the key and try again.")
                    except requests.RequestException:
                        st.error("Network error while contacting Perplexity.")
                    except Exception:
                        st.error("Unexpected error during execution.")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.perplexity_result:
                st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
                st.subheader("Perplexity Result")
                st.write(st.session_state.perplexity_result)

                if st.session_state.perplexity_citations:
                    st.markdown("**Citations**")
                    for idx, url in enumerate(st.session_state.perplexity_citations, start=1):
                        st.markdown(f"{idx}. {url}")
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

            st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
            st.subheader("Security Notes")
            st.write("- Production keys should go in Railway Variables.")
            st.write("- Temporary key entry is for testing only.")
            st.write("- Secrets are never displayed back in the UI.")
            st.write("- Input for typed tool identifiers is restricted to simple characters.")
            st.markdown('</div>', unsafe_allow_html=True)
