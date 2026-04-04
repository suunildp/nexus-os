import copy
import re
import time
import uuid
import streamlit as st

st.set_page_config(
    page_title="Nexus OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
:root {
    --panel-bg: rgba(255,255,255,0.03);
    --panel-border: rgba(120,120,120,0.18);
    --panel-border-strong: rgba(147,197,253,0.22);
    --text-muted: #8f8f8f;
    --text-soft: #b8b8b8;
    --ok: #86efac;
    --warn: #fbbf24;
    --live: #4ade80;
    --manual: #fbbf24;
    --demo: #93c5fd;
}

.block-container {
    padding-top: 0.65rem;
    padding-bottom: 1.4rem;
    max-width: 1040px;
}

section[data-testid="stSidebar"] > div {
    padding-top: 1rem;
}

div[data-testid="stVerticalBlock"] > div:has(> div.nexus-card) {
    margin-bottom: 0.55rem;
}

.nexus-card {
    padding: 0.95rem 1rem;
    border: 1px solid var(--panel-border);
    border-radius: 14px;
    margin-bottom: 0.75rem;
    background: var(--panel-bg);
}

.hero-card {
    padding-top: 0.8rem;
    padding-bottom: 0.8rem;
}

.small-muted {
    color: var(--text-muted);
    font-size: 0.9rem;
    line-height: 1.45;
}

.section-title {
    margin-bottom: 0.2rem;
}

.inline-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.35rem;
}

.tag {
    display: inline-flex;
    align-items: center;
    padding: 0.28rem 0.62rem;
    border-radius: 999px;
    border: 1px solid rgba(120,120,120,0.24);
    font-size: 0.8rem;
    line-height: 1.2;
    color: #d7d7d7;
    background: rgba(255,255,255,0.02);
}

.path-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.55rem;
    margin-bottom: 0.75rem;
}

.step-chip {
    display: inline-flex;
    align-items: center;
    padding: 0.42rem 0.72rem;
    border-radius: 999px;
    font-size: 0.82rem;
    border: 1px solid rgba(120,120,120,0.22);
    white-space: nowrap;
}

.step-done {
    background: rgba(74, 222, 128, 0.12);
    color: var(--ok);
}

.step-now {
    background: rgba(147, 197, 253, 0.12);
    color: var(--demo);
}

.step-later {
    background: rgba(255,255,255,0.02);
    color: var(--text-soft);
}

.next-box {
    padding: 0.8rem 0.9rem;
    border-radius: 12px;
    border: 1px solid var(--panel-border-strong);
    background: rgba(147,197,253,0.05);
    margin-top: 0.2rem;
}

.step-card {
    padding: 0.78rem 0.9rem;
    border: 1px solid var(--panel-border);
    border-radius: 12px;
    margin-bottom: 0.6rem;
    background: rgba(255,255,255,0.018);
}

.meta-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
    margin: 0.15rem 0 0.35rem 0;
    color: var(--text-muted);
    font-size: 0.82rem;
}

.ok { color: var(--ok); font-weight: 600; }
.warn { color: var(--warn); font-weight: 600; }
.mode-live { color: var(--live); font-weight: 600; }
.mode-manual { color: var(--manual); font-weight: 600; }
.mode-demo { color: var(--demo); font-weight: 600; }

.compact-note {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: -0.25rem;
    margin-bottom: 0.45rem;
}

div[data-testid="stTextArea"] textarea {
    min-height: 100px;
}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div,
div[data-testid="stMultiSelect"] > div,
div[data-testid="stTextArea"] textarea {
    border-radius: 10px;
}

div[data-testid="stExpander"] {
    border: 1px solid var(--panel-border);
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
}

hr {
    margin-top: 0.7rem !important;
    margin-bottom: 0.7rem !important;
}

h1 {
    margin-bottom: 0.15rem !important;
}

h2, h3 {
    margin-bottom: 0.1rem !important;
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 0.55rem;
        padding-bottom: 1rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }

    .nexus-card {
        padding: 0.82rem 0.85rem;
        border-radius: 12px;
        margin-bottom: 0.65rem;
    }

    h1 {
        font-size: 1.72rem !important;
    }

    .step-chip {
        font-size: 0.77rem;
        padding: 0.38rem 0.6rem;
    }

    .tag {
        font-size: 0.76rem;
    }

    .next-box {
        padding: 0.72rem 0.8rem;
    }
}
</style>
""", unsafe_allow_html=True)

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

DEMO_TOOL_BEHAVIOR = {
    "Perplexity": "Research and source discovery",
    "Gemini": "Drafting and synthesis",
    "Claude": "Reasoning and structured writing",
    "ChatGPT": "General drafting and iteration",
    "Julius AI": "Analysis and data interpretation",
    "Canva": "Visual formatting and design output",
    "Gamma AI": "Deck generation and narrative slides",
    "AIPPT": "Presentation generation",
    "NotebookLM": "Source digestion and note grounding",
    "Grok": "Fast angle generation",
    "Merlin": "Quick assistant support"
}

DEFAULT_CONNECTOR_MODES = {
    "Perplexity": "Demo",
    "Gemini": "Manual",
    "Claude": "Manual",
    "ChatGPT": "Manual",
    "Julius AI": "Manual",
    "Canva": "Manual",
    "Gamma AI": "Manual",
    "AIPPT": "Manual",
    "NotebookLM": "Manual",
    "Grok": "Manual",
    "Merlin": "Manual"
}

DEFAULT_STATE = {
    "goal": "",
    "output_format": "Text",
    "optimization_pref": "Accuracy",
    "selected_stack": [],
    "suggested_stack": [],
    "alternative_stack": [],
    "recognized_tools": [],
    "unrecognized_tools": [],
    "workflow_confirmed": False,
    "objective_input": "",
    "objective_widget": "",
    "workflow_steps": [],
    "execution_log": [],
    "final_artifact": "",
    "run_counter": 0,
    "connector_modes": copy.deepcopy(DEFAULT_CONNECTOR_MODES),
}

for key, value in DEFAULT_STATE.items():
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
    return ["Perplexity"], ["Gemini", "Claude", "ChatGPT"]

def parse_tool_identifiers(raw_text):
    cleaned = raw_text.strip().lower()
    if not cleaned:
        return [], []
    if len(cleaned) > 200:
        return [], ["input too long"]
    if not re.fullmatch(r"[a-z0-9,\-\s]+", cleaned):
        return [], ["invalid characters in tool input"]

    parts = [p.strip() for p in cleaned.split(",") if p.strip()]
    recognized, unrecognized = [], []

    for part in parts:
        if part in TOOL_ALIAS_MAP:
            mapped = TOOL_ALIAS_MAP[part]
            if mapped not in recognized:
                recognized.append(mapped)
        else:
            unrecognized.append(part)

    return recognized, unrecognized

def build_default_workflow(goal, stack):
    if not stack:
        return []

    templates = {
        "Deep research only": [
            ("Research brief", stack[0], "Collect facts, questions, and source directions"),
            ("Evidence distillation", stack[1] if len(stack) > 1 else stack[0], "Condense findings into usable notes"),
            ("Final research memo", stack[0], "Produce a coherent final answer pack"),
        ],
        "Research + blog / long-form": [
            ("Research discovery", stack[0], "Gather facts, themes, and source directions"),
            ("Outline and argument", stack[1] if len(stack) > 1 else stack[0], "Turn research into a clear content structure"),
            ("Long-form draft", stack[1] if len(stack) > 1 else stack[0], "Generate a polished article draft"),
        ],
        "Research + AI agent / prompt / config": [
            ("Research discovery", stack[0], "Gather relevant patterns, examples, and source logic"),
            ("System design draft", stack[1] if len(stack) > 1 else stack[0], "Convert findings into an agent or prompt structure"),
            ("Final prompt pack", stack[1] if len(stack) > 1 else stack[0], "Produce deployable prompt/config output"),
        ],
        "Research + slide deck / pitch": [
            ("Research discovery", stack[0], "Collect facts, angles, and supporting points"),
            ("Narrative shaping", stack[0], "Organize a story arc for the pitch"),
            ("Deck generation", stack[1] if len(stack) > 1 else stack[0], "Create the slide-ready structure"),
        ],
        "Research + social media sequence": [
            ("Topic research", stack[0], "Identify themes, talking points, and positioning"),
            ("Content adaptation", stack[1] if len(stack) > 1 else stack[0], "Convert the research into post-ready pieces"),
            ("Final sequence", stack[1] if len(stack) > 1 else stack[0], "Produce the social post set"),
        ],
        "Custom": [
            ("Step 1", stack[0], "Define the first handoff"),
            ("Step 2", stack[1] if len(stack) > 1 else stack[0], "Define the second handoff"),
            ("Step 3", stack[0], "Define the final output stage"),
        ],
    }

    chosen = templates.get(goal, templates["Custom"])
    steps = []
    for idx, (name, tool, purpose) in enumerate(chosen, start=1):
        steps.append({
            "id": str(uuid.uuid4())[:8],
            "order": idx,
            "name": name,
            "tool": tool,
            "purpose": purpose,
            "input_from": "User objective" if idx == 1 else f"Step {idx-1}",
            "output_label": f"Step {idx} output",
        })
    return steps

def resequence_steps():
    for idx, step in enumerate(st.session_state.workflow_steps, start=1):
        step["order"] = idx
        if idx == 1:
            step["input_from"] = "User objective"
        elif step["input_from"] not in [f"Step {i}" for i in range(1, len(st.session_state.workflow_steps) + 1)]:
            step["input_from"] = f"Step {idx-1}"

def add_workflow_step():
    next_index = len(st.session_state.workflow_steps) + 1
    fallback_tool = st.session_state.selected_stack[0] if st.session_state.selected_stack else "Perplexity"
    st.session_state.workflow_steps.append({
        "id": str(uuid.uuid4())[:8],
        "order": next_index,
        "name": f"Step {next_index}",
        "tool": fallback_tool,
        "purpose": "Describe what this step does",
        "input_from": "User objective" if next_index == 1 else f"Step {next_index-1}",
        "output_label": f"Step {next_index} output",
    })

def remove_last_step():
    if st.session_state.workflow_steps:
        st.session_state.workflow_steps.pop()
        resequence_steps()

def validate_workflow():
    objective = st.session_state.get("objective_widget", "").strip()

    if not st.session_state.goal:
        return False, "Please choose a primary goal."
    if not st.session_state.selected_stack:
        return False, "Please choose at least one tool."
    if not objective:
        return False, "Please enter your objective."
    if not st.session_state.workflow_steps:
        return False, "Please generate or review the workflow."

    for step in st.session_state.workflow_steps:
        if not step["name"].strip():
            return False, f"Step {step['order']} needs a name."
        if not step["purpose"].strip():
            return False, f"Step {step['order']} needs a purpose."
        if step["tool"] not in TOOL_OPTIONS:
            return False, f"Step {step['order']} has an invalid tool."

    st.session_state.objective_input = objective
    return True, "Workflow looks good."

def simulate_step_output(step, objective, prior_output):
    mode = st.session_state.connector_modes.get(step["tool"], "Demo")
    behavior = DEMO_TOOL_BEHAVIOR.get(step["tool"], "General processing")
    inherited = " It used the previous handoff to refine the next deliverable." if prior_output else ""

    return (
        f"{step['tool']} handled '{step['name']}' for the objective: {objective}. "
        f"Purpose: {step['purpose']}. "
        f"Input source: {step['input_from']}. "
        f"Connector mode: {mode}. "
        f"Simulated role: {behavior}.{inherited}"
    )

def run_demo_workflow():
    st.session_state.execution_log = []
    st.session_state.final_artifact = ""
    prior_output = ""
    objective = st.session_state.get("objective_widget", "").strip()

    progress = st.progress(0, text="Starting orchestration...")
    total_steps = len(st.session_state.workflow_steps)

    for idx, step in enumerate(st.session_state.workflow_steps, start=1):
        step_output = simulate_step_output(step, objective, prior_output)
        st.session_state.execution_log.append({
            "step": step["order"],
            "name": step["name"],
            "tool": step["tool"],
            "mode": st.session_state.connector_modes.get(step["tool"], "Demo"),
            "input_from": step["input_from"],
            "purpose": step["purpose"],
            "status": "Completed",
            "output": step_output,
        })
        prior_output = step_output
        pct = int((idx / total_steps) * 100)
        progress.progress(pct, text=f"Running step {idx} of {total_steps}: {step['name']}")
        time.sleep(0.25)

    progress.empty()

    artifact_lines = [
        f"Objective: {objective}",
        f"Goal type: {st.session_state.goal}",
        f"Output format requested: {st.session_state.output_format}",
        "",
        "Orchestration summary:",
    ]

    for item in st.session_state.execution_log:
        artifact_lines.append(
            f"{item['step']}. {item['name']} | Tool: {item['tool']} | Mode: {item['mode']} | Outcome: {item['output']}"
        )

    artifact_lines.append("")
    artifact_lines.append("Final artifact preview:")
    artifact_lines.append("This is a simulated final artifact representing the combined result of the selected tool chain.")

    st.session_state.final_artifact = "\n".join(artifact_lines)
    st.session_state.run_counter += 1

def mode_badge(mode):
    if mode == "Live":
        return "<span class='mode-live'>Live</span>"
    if mode == "Manual":
        return "<span class='mode-manual'>Manual</span>"
    return "<span class='mode-demo'>Demo</span>"

def get_current_stage():
    if not st.session_state.goal:
        return 1
    if not st.session_state.selected_stack:
        return 2
    if not st.session_state.objective_widget.strip():
        return 4
    return 5

def next_action_message():
    if not st.session_state.goal:
        return "Choose your primary goal to generate a recommended workflow."
    if not st.session_state.selected_stack:
        return "Confirm the tools you want in this workflow."
    if not st.session_state.objective_widget.strip():
        return "Describe the result you want Nexus OS to produce."
    if not st.session_state.workflow_confirmed:
        return "Review the workflow, validate it, then run the orchestrator."
    return "You are ready to run the orchestrator."

st.title("🧠 Nexus OS")
st.caption("A guided orchestrator for multi-tool workflows")

with st.sidebar:
    st.header("System")
    st.write("Nexus OS MVP")
    st.caption("Polished stable fallback mode")

    if st.button("Reset app"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown("### Current stack")
    if st.session_state.selected_stack:
        for tool in st.session_state.selected_stack:
            mode = st.session_state.connector_modes.get(tool, "Demo")
            st.markdown(f"**{tool}** — {mode_badge(mode)}", unsafe_allow_html=True)
    else:
        st.caption("No tools selected yet.")

st.markdown('<div class="nexus-card hero-card">', unsafe_allow_html=True)
st.subheader("Setup path")
st.markdown('<div class="small-muted">A tighter guided flow with optional advanced editing.</div>', unsafe_allow_html=True)

current_stage = get_current_stage()
step_labels = ["1. Goal", "2. Stack", "3. Modes", "4. Objective", "5. Review & Run"]

st.markdown('<div class="path-wrap">', unsafe_allow_html=True)
for idx, label in enumerate(step_labels, start=1):
    if idx < current_stage:
        cls = "step-chip step-done"
    elif idx == current_stage:
        cls = "step-chip step-now"
    else:
        cls = "step-chip step-later"
    st.markdown(f"<span class='{cls}'>{label}</span>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="next-box">', unsafe_allow_html=True)
st.write(f"**Recommended next action:** {next_action_message()}")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">', unsafe_allow_html=True)
st.subheader("1. Goal and output")
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="small-muted">Start here to generate a recommended stack and starter workflow.</div>', unsafe_allow_html=True)

goal_index = GOAL_OPTIONS.index(st.session_state.goal) if st.session_state.goal in GOAL_OPTIONS else 0
chosen_goal = st.selectbox("Primary goal", GOAL_OPTIONS, index=goal_index)

output_options = ["Text", "Markdown", "JSON", "Slide Outline", "Agent Prompt"]
output_index = output_options.index(st.session_state.output_format) if st.session_state.output_format in output_options else 0
chosen_output = st.selectbox("Desired output", output_options, index=output_index)

opt_options = ["Accuracy", "Speed", "Cost", "Balanced"]
opt_index = opt_options.index(st.session_state.optimization_pref) if st.session_state.optimization_pref in opt_options else 0
chosen_opt = st.selectbox("Optimize for", opt_options, index=opt_index)

if st.button("Save goal and generate stack", type="primary"):
    suggested, alternatives = get_tool_recommendations(chosen_goal)
    st.session_state.goal = chosen_goal
    st.session_state.output_format = chosen_output
    st.session_state.optimization_pref = chosen_opt
    st.session_state.suggested_stack = suggested
    st.session_state.selected_stack = suggested.copy()
    st.session_state.alternative_stack = alternatives
    st.session_state.workflow_steps = build_default_workflow(chosen_goal, suggested)
    st.session_state.workflow_confirmed = False
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.goal:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("2. Tool stack")

    if st.session_state.suggested_stack:
        st.markdown('<div class="small-muted">Suggested tools</div>', unsafe_allow_html=True)
        st.markdown('<div class="inline-tags">', unsafe_allow_html=True)
        for tool in st.session_state.suggested_stack:
            st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.alternative_stack:
        with st.expander("Show alternatives", expanded=False):
            st.markdown('<div class="inline-tags">', unsafe_allow_html=True)
            for tool in st.session_state.alternative_stack:
                st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.selected_stack = st.multiselect(
        "Choose the tools you want in this workflow",
        TOOL_OPTIONS,
        default=st.session_state.selected_stack
    )

    with st.expander("Optional: add tools by typing names", expanded=False):
        raw_tool_input = st.text_input("Typed tools", placeholder="Example: canva, merlin")
        if st.button("Add typed tools"):
            recognized, unrecognized = parse_tool_identifiers(raw_tool_input)
            st.session_state.recognized_tools = recognized
            st.session_state.unrecognized_tools = unrecognized
            st.session_state.selected_stack = list(dict.fromkeys(st.session_state.selected_stack + recognized))
            if not st.session_state.workflow_steps:
                st.session_state.workflow_steps = build_default_workflow(st.session_state.goal, st.session_state.selected_stack)
            st.rerun()

        if st.session_state.recognized_tools:
            st.caption("Recognized tools: " + ", ".join(st.session_state.recognized_tools))
        if st.session_state.unrecognized_tools:
            st.caption("Unrecognized entries: " + ", ".join(st.session_state.unrecognized_tools))

    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.selected_stack:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("3. Connector modes")
    st.markdown('<div class="small-muted">Keep it practical: Live = API, Manual = human handoff, Demo = simulated connector.</div>', unsafe_allow_html=True)

    for tool in st.session_state.selected_stack:
        st.markdown(f"**{tool}**", unsafe_allow_html=True)
        st.markdown('<div class="compact-note">Choose how this tool participates right now.</div>', unsafe_allow_html=True)
        st.session_state.connector_modes[tool] = st.selectbox(
            f"Mode for {tool}",
            ["Live", "Manual", "Demo"],
            index=["Live", "Manual", "Demo"].index(st.session_state.connector_modes.get(tool, "Demo")),
            key=f"mode_{tool}",
            label_visibility="collapsed"
        )

    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.selected_stack:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("4. Objective")
    st.markdown('<div class="small-muted">Describe the final result you want. Keep it outcome-oriented and specific.</div>', unsafe_allow_html=True)

    if not st.session_state.objective_widget and st.session_state.objective_input:
        st.session_state.objective_widget = st.session_state.objective_input

    st.text_area(
        "What should Nexus OS produce?",
        key="objective_widget",
        placeholder="Example: Pitch deck for solution on impact of AI to reduce training timelines.",
        max_chars=3000,
        height=118
    )

    st.session_state.objective_input = st.session_state.objective_widget
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.selected_stack:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("5. Review and run")
    st.markdown('<div class="small-muted">Review the starter workflow below. Only expand advanced editing if you need to fine-tune the handoffs.</div>', unsafe_allow_html=True)

    if not st.session_state.workflow_steps:
        st.session_state.workflow_steps = build_default_workflow(
            st.session_state.goal or "Custom",
            st.session_state.selected_stack or ["Perplexity"]
        )

    for step in st.session_state.workflow_steps:
        mode = st.session_state.connector_modes.get(step["tool"], "Demo")
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.write(f"**Step {step['order']}: {step['name']}**")
        st.markdown(
            f"<div class='meta-row'><span>Tool: {step['tool']}</span><span>Mode: {mode}</span><span>Input: {step['input_from']}</span></div>",
            unsafe_allow_html=True
        )
        st.write(step["purpose"])
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("Advanced workflow editing", expanded=False):
        if st.button("Add step"):
            add_workflow_step()
            st.rerun()

        if st.button("Remove last step"):
            remove_last_step()
            st.rerun()

        if st.button("Reload recommended workflow"):
            st.session_state.workflow_steps = build_default_workflow(
                st.session_state.goal or "Custom",
                st.session_state.selected_stack or ["Perplexity"]
            )
            st.session_state.workflow_confirmed = False
            st.rerun()

        for idx, step in enumerate(st.session_state.workflow_steps):
            st.markdown('<div class="step-card">', unsafe_allow_html=True)
            st.markdown(f"**Advanced edit: Step {idx + 1}**", unsafe_allow_html=True)

            step["name"] = st.text_input(
                f"Step {idx + 1} name",
                value=step["name"],
                key=f"name_{step['id']}"
            )
            step["tool"] = st.selectbox(
                f"Tool for step {idx + 1}",
                TOOL_OPTIONS,
                index=TOOL_OPTIONS.index(step["tool"]) if step["tool"] in TOOL_OPTIONS else 0,
                key=f"tool_{step['id']}"
            )
            step["purpose"] = st.text_area(
                f"Purpose for step {idx + 1}",
                value=step["purpose"],
                key=f"purpose_{step['id']}",
                height=96
            )

            input_choices = ["User objective"] + [f"Step {i}" for i in range(1, len(st.session_state.workflow_steps) + 1) if i != idx + 1]
            if step["input_from"] not in input_choices:
                step["input_from"] = "User objective" if idx == 0 else f"Step {idx}"
            step["input_from"] = st.selectbox(
                f"Input source for step {idx + 1}",
                input_choices,
                index=input_choices.index(step["input_from"]),
                key=f"input_{step['id']}"
            )
            step["output_label"] = st.text_input(
                f"Output label for step {idx + 1}",
                value=step["output_label"],
                key=f"output_{step['id']}"
            )
            st.markdown('</div>', unsafe_allow_html=True)

    resequence_steps()

    if st.button("Validate workflow", type="primary"):
        ok, message = validate_workflow()
        if ok:
            st.session_state.workflow_confirmed = True
            st.success(message)
        else:
            st.session_state.workflow_confirmed = False
            st.error(message)

    if st.button("Run orchestrator"):
        ok, message = validate_workflow()
        if not ok:
            st.session_state.workflow_confirmed = False
            st.error(message)
        else:
            st.session_state.workflow_confirmed = True
            run_demo_workflow()
            st.success("Demo workflow completed.")

    if st.session_state.workflow_confirmed:
        st.markdown("<span class='ok'>Ready and validated.</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='warn'>Validate once before running.</span>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.execution_log:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Execution log")
    for item in st.session_state.execution_log:
        with st.expander(f"Step {item['step']} · {item['name']} · {item['tool']}", expanded=False):
            st.write(f"**Mode:** {item['mode']}")
            st.write(f"**Input from:** {item['input_from']}")
            st.write(f"**Purpose:** {item['purpose']}")
            st.write(f"**Status:** {item['status']}")
            st.write(f"**Output:** {item['output']}")
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.final_artifact:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Final artifact")
    st.text_area(
        "Artifact preview",
        value=st.session_state.final_artifact,
        height=170,
        disabled=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

with st.expander("Plan snapshot", expanded=False):
    st.write(f"**Goal:** {st.session_state.goal or 'Not set'}")
    st.write(f"**Output format:** {st.session_state.output_format}")
    st.write(f"**Optimization:** {st.session_state.optimization_pref}")
    st.write(f"**Run count:** {st.session_state.run_counter}")

with st.expander("Operating model", expanded=False):
    st.write("- Live = real API or direct integrated execution.")
    st.write("- Manual = you use the tool yourself and Nexus OS tracks the handoff.")
    st.write("- Demo = simulated execution while refining the orchestration logic.")
