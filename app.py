import copy
import re
import time
import uuid
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
    max-width: 1200px;
}
.nexus-card {
    padding: 1rem 1.25rem;
    border: 1px solid rgba(120,120,120,0.18);
    border-radius: 14px;
    margin-bottom: 1rem;
    background: rgba(255,255,255,0.03);
}
.small-muted {
    color: #8a8a8a;
    font-size: 0.92rem;
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
.step-card {
    padding: 0.9rem 1rem;
    border: 1px solid rgba(120,120,120,0.18);
    border-radius: 12px;
    margin-bottom: 0.9rem;
    background: rgba(255,255,255,0.02);
}
.ok {
    color: #4ade80;
    font-weight: 600;
}
.warn {
    color: #fbbf24;
    font-weight: 600;
}
.info {
    color: #93c5fd;
    font-weight: 600;
}
.err {
    color: #f87171;
    font-weight: 600;
}
.mono {
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-size: 0.88rem;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Nexus OS")
st.caption("Orchestrate your multi-tool workflow from one place")

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

default_state = {
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
    "workflow_steps": [],
    "execution_log": [],
    "final_artifact": "",
    "run_counter": 0
}

for key, value in default_state.items():
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

def build_default_workflow(goal, stack):
    if not stack:
        return []

    step_templates = {
        "Deep research only": [
            ("Research brief", stack[0], "Collect facts, questions, and source directions"),
            ("Evidence distillation", stack[1] if len(stack) > 1 else stack[0], "Condense findings into usable notes"),
            ("Final research memo", stack[0], "Produce a coherent final answer pack")
        ],
        "Research + blog / long-form": [
            ("Research discovery", stack[0], "Gather facts, themes, and source directions"),
            ("Outline and argument", stack[1] if len(stack) > 1 else stack[0], "Turn research into a clear content structure"),
            ("Long-form draft", stack[1] if len(stack) > 1 else stack[0], "Generate a polished article draft")
        ],
        "Research + AI agent / prompt / config": [
            ("Research discovery", stack[0], "Gather relevant patterns, examples, and source logic"),
            ("System design draft", stack[1] if len(stack) > 1 else stack[0], "Convert findings into an agent or prompt structure"),
            ("Final prompt pack", stack[1] if len(stack) > 1 else stack[0], "Produce deployable prompt/config output")
        ],
        "Research + slide deck / pitch": [
            ("Research discovery", stack[0], "Collect facts, angles, and supporting points"),
            ("Narrative shaping", stack[0], "Organize a story arc for the pitch"),
            ("Deck generation", stack[1] if len(stack) > 1 else stack[0], "Create the slide-ready structure")
        ],
        "Research + social media sequence": [
            ("Topic research", stack[0], "Identify themes, talking points, and positioning"),
            ("Content adaptation", stack[1] if len(stack) > 1 else stack[0], "Convert the research into post-ready pieces"),
            ("Final sequence", stack[1] if len(stack) > 1 else stack[0], "Produce the social post set")
        ],
        "Custom": [
            ("Step 1", stack[0], "Define the first handoff"),
            ("Step 2", stack[1] if len(stack) > 1 else stack[0], "Define the second handoff"),
            ("Step 3", stack[0], "Define the final output stage")
        ]
    }

    chosen = step_templates.get(goal, step_templates["Custom"])
    workflow = []
    for idx, (name, tool, purpose) in enumerate(chosen, start=1):
        workflow.append({
            "id": str(uuid.uuid4())[:8],
            "order": idx,
            "name": name,
            "tool": tool,
            "purpose": purpose,
            "input_from": "User objective" if idx == 1 else f"Step {idx-1}",
            "status": "Ready",
            "output_label": f"Step {idx} output"
        })
    return workflow

def add_workflow_step():
    next_index = len(st.session_state.workflow_steps) + 1
    fallback_tool = st.session_state.selected_stack[0] if st.session_state.selected_stack else "Perplexity"
    st.session_state.workflow_steps.append({
        "id": str(uuid.uuid4())[:8],
        "order": next_index,
        "name": f"Step {next_index}",
        "tool": fallback_tool,
        "purpose": "Describe what this step does",
        "input_from": f"Step {next_index-1}" if next_index > 1 else "User objective",
        "status": "Ready",
        "output_label": f"Step {next_index} output"
    })

def remove_last_step():
    if st.session_state.workflow_steps:
        st.session_state.workflow_steps.pop()
        resequence_steps()

def resequence_steps():
    for idx, step in enumerate(st.session_state.workflow_steps, start=1):
        step["order"] = idx
        if idx == 1:
            step["input_from"] = "User objective"
        elif step["input_from"] not in [f"Step {i}" for i in range(1, len(st.session_state.workflow_steps) + 1)]:
            step["input_from"] = f"Step {idx-1}"

def validate_workflow():
    if not st.session_state.objective_input.strip():
        return False, "Please enter your objective."
    if not st.session_state.workflow_steps:
        return False, "Please add at least one workflow step."

    for step in st.session_state.workflow_steps:
        if not step["name"].strip():
            return False, f"Step {step['order']} needs a name."
        if not step["purpose"].strip():
            return False, f"Step {step['order']} needs a purpose."
        if step["tool"] not in TOOL_OPTIONS:
            return False, f"Step {step['order']} has an invalid tool."
    return True, "Workflow looks good."

def simulate_step_output(step, objective, prior_output):
    base = f"{step['tool']} handled '{step['name']}' for the objective: {objective.strip()}."
    purpose = f" Purpose: {step['purpose'].strip()}."
    chain = f" Input source: {step['input_from']}."
    inherited = ""
    if prior_output:
        inherited = f" It used the previous handoff to refine the next deliverable."
    behavior = DEMO_TOOL_BEHAVIOR.get(step["tool"], "General processing")
    return f"{base}{purpose}{chain} Simulated role: {behavior}.{inherited}"

def run_demo_workflow():
    st.session_state.execution_log = []
    st.session_state.final_artifact = ""
    prior_output = ""

    progress = st.progress(0, text="Starting orchestration...")
    total_steps = len(st.session_state.workflow_steps)

    for idx, step in enumerate(st.session_state.workflow_steps, start=1):
        step_output = simulate_step_output(step, st.session_state.objective_input, prior_output)
        log_item = {
            "step": step["order"],
            "name": step["name"],
            "tool": step["tool"],
            "input_from": step["input_from"],
            "purpose": step["purpose"],
            "status": "Completed",
            "output": step_output
        }
        st.session_state.execution_log.append(log_item)
        prior_output = step_output
        pct = int((idx / total_steps) * 100)
        progress.progress(pct, text=f"Running step {idx} of {total_steps}: {step['name']}")
        time.sleep(0.35)

    progress.empty()

    artifact_lines = [
        f"Objective: {st.session_state.objective_input.strip()}",
        f"Goal type: {st.session_state.goal or 'Not specified'}",
        f"Output format requested: {st.session_state.output_format}",
        "",
        "Orchestration summary:"
    ]

    for item in st.session_state.execution_log:
        artifact_lines.append(
            f"{item['step']}. {item['name']} | Tool: {item['tool']} | Outcome: {item['output']}"
        )

    artifact_lines.append("")
    artifact_lines.append("Final artifact preview:")
    artifact_lines.append(
        "This is a simulated final artifact representing the combined result of the selected tool chain."
    )

    st.session_state.final_artifact = "\n".join(artifact_lines)
    st.session_state.run_counter += 1

with st.sidebar:
    st.header("System")
    st.write("Nexus OS MVP")
    st.caption("Demo orchestration mode")

    if st.button("Reset app"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown("### Mode")
    st.markdown("<span class='info'>Demo orchestration</span>", unsafe_allow_html=True)
    st.caption("This version models your workflow and handoffs before live APIs are added.")

    st.markdown("### Current stack")
    if st.session_state.selected_stack:
        for tool in st.session_state.selected_stack:
            st.markdown(f"<span class='tag'>{tool}</span>", unsafe_allow_html=True)
    else:
        st.caption("No tools selected yet.")

st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
st.subheader("Workflow setup")
st.markdown('<div class="small-muted">Choose the outcome you want, the stack you prefer, and let Nexus OS model the handoff chain.</div>', unsafe_allow_html=True)

col_a, col_b, col_c = st.columns(3)
with col_a:
    goal = st.selectbox("Primary goal", GOAL_OPTIONS, index=0 if not st.session_state.goal else GOAL_OPTIONS.index(st.session_state.goal))
with col_b:
    output_format = st.selectbox("Desired output", ["Text", "Markdown", "JSON", "Slide Outline", "Agent Prompt"])
with col_c:
    optimization_pref = st.selectbox("Optimize for", ["Accuracy", "Speed", "Cost", "Balanced"])

if st.button("Generate suggested stack", type="primary"):
    suggested, alternatives = get_tool_recommendations(goal)
    st.session_state.goal = goal
    st.session_state.output_format = output_format
    st.session_state.optimization_pref = optimization_pref
    st.session_state.suggested_stack = suggested
    st.session_state.selected_stack = suggested.copy()
    st.session_state.alternative_stack = alternatives
    st.session_state.workflow_steps = build_default_workflow(goal, suggested)
    st.session_state.workflow_confirmed = False
    st.rerun()

if st.session_state.suggested_stack:
    st.markdown('<div class="section-label">Suggested stack</div>', unsafe_allow_html=True)
    for tool in st.session_state.suggested_stack:
        st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

    if st.session_state.alternative_stack:
        st.markdown('<div class="section-label">Alternatives</div>', unsafe_allow_html=True)
        for tool in st.session_state.alternative_stack:
            st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)

    raw_tool_input = st.text_input(
        "Add tools by identifier or name (comma-separated)",
        placeholder="Example: perplexity, gamma, canva"
    )

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Recognize typed tools"):
            recognized, unrecognized = parse_tool_identifiers(raw_tool_input)
            st.session_state.recognized_tools = recognized
            st.session_state.unrecognized_tools = unrecognized
            merged = list(dict.fromkeys(st.session_state.selected_stack + recognized))
            st.session_state.selected_stack = merged
            if not st.session_state.workflow_steps:
                st.session_state.workflow_steps = build_default_workflow(st.session_state.goal, merged)
            st.rerun()
    with col2:
        selected_stack = st.multiselect(
            "Selected tool stack",
            TOOL_OPTIONS,
            default=st.session_state.selected_stack
        )
        st.session_state.selected_stack = selected_stack

    if st.session_state.recognized_tools:
        st.caption("Recognized tools: " + ", ".join(st.session_state.recognized_tools))
    if st.session_state.unrecognized_tools:
        st.caption("Unrecognized entries: " + ", ".join(st.session_state.unrecognized_tools))

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
st.subheader("Objective")
st.session_state.objective_input = st.text_area(
    "Describe the result you want Nexus OS to produce",
    value=st.session_state.objective_input,
    placeholder="Example: Research AI adoption in India, draft a blog post, then convert it into a slide-ready outline.",
    max_chars=3000,
    height=120
)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
st.subheader("Workflow builder")
st.markdown('<div class="small-muted">Edit the handoff chain so it mirrors how you currently jump between tools.</div>', unsafe_allow_html=True)

col_x, col_y, col_z = st.columns([1, 1, 2])
with col_x:
    if st.button("Add step"):
        add_workflow_step()
        st.rerun()
with col_y:
    if st.button("Remove last step"):
        remove_last_step()
        st.rerun()
with col_z:
    if st.button("Load default workflow"):
        st.session_state.workflow_steps = build_default_workflow(
            st.session_state.goal or "Custom",
            st.session_state.selected_stack or ["Perplexity"]
        )
        st.rerun()

if not st.session_state.workflow_steps and st.session_state.selected_stack:
    st.session_state.workflow_steps = build_default_workflow(
        st.session_state.goal or "Custom",
        st.session_state.selected_stack
    )

for idx, step in enumerate(st.session_state.workflow_steps):
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown(f"**Step {idx + 1}**")

    c1, c2 = st.columns([2, 1])
    with c1:
        step["name"] = st.text_input(
            f"Step {idx + 1} name",
            value=step["name"],
            key=f"name_{step['id']}"
        )
    with c2:
        step["tool"] = st.selectbox(
            f"Tool for step {idx + 1}",
            TOOL_OPTIONS,
            index=TOOL_OPTIONS.index(step["tool"]) if step["tool"] in TOOL_OPTIONS else 0,
            key=f"tool_{step['id']}"
        )

    c3, c4 = st.columns([2, 1])
    with c3:
        step["purpose"] = st.text_area(
            f"Purpose for step {idx + 1}",
            value=step["purpose"],
            key=f"purpose_{step['id']}",
            height=90
        )
    with c4:
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

    st.caption(f"Simulated role: {DEMO_TOOL_BEHAVIOR.get(step['tool'], 'General processing')}")
    st.markdown('</div>', unsafe_allow_html=True)

resequence_steps()

col_v1, col_v2 = st.columns([1, 2])
with col_v1:
    if st.button("Validate workflow", type="primary"):
        ok, message = validate_workflow()
        if ok:
            st.session_state.workflow_confirmed = True
            st.success(message)
        else:
            st.session_state.workflow_confirmed = False
            st.error(message)
with col_v2:
    if st.session_state.workflow_confirmed:
        st.markdown("<span class='ok'>Workflow validated and ready to simulate.</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='warn'>Validate the workflow before running it.</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

col_main, col_side = st.columns([1.4, 1])

with col_main:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Execution")
    st.markdown('<div class="small-muted">Run the workflow in demo mode to inspect each handoff and the resulting artifact.</div>', unsafe_allow_html=True)

    if st.button("Run orchestrator", type="primary"):
        ok, message = validate_workflow()
        if not ok:
            st.session_state.workflow_confirmed = False
            st.error(message)
        else:
            st.session_state.workflow_confirmed = True
            run_demo_workflow()
            st.success("Demo workflow completed.")

    if st.session_state.execution_log:
        st.markdown('<div class="section-label">Execution log</div>', unsafe_allow_html=True)
        for item in st.session_state.execution_log:
            with st.expander(f"Step {item['step']} · {item['name']} · {item['tool']}", expanded=False):
                st.write(f"**Input from:** {item['input_from']}")
                st.write(f"**Purpose:** {item['purpose']}")
                st.write(f"**Status:** {item['status']}")
                st.write(f"**Output:** {item['output']}")
    else:
        st.caption("No run yet. Once you simulate the workflow, each tool handoff will appear here.")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.final_artifact:
        st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
        st.subheader("Final artifact")
        st.text_area(
            "Artifact preview",
            value=st.session_state.final_artifact,
            height=320,
            disabled=True
        )
        st.markdown('</div>', unsafe_allow_html=True)

with col_side:
    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Plan snapshot")
    st.write(f"**Goal:** {st.session_state.goal or 'Not set'}")
    st.write(f"**Output format:** {st.session_state.output_format}")
    st.write(f"**Optimization:** {st.session_state.optimization_pref}")
    st.write(f"**Run count:** {st.session_state.run_counter}")

    st.markdown("**Stack in play:**")
    if st.session_state.selected_stack:
        for tool in st.session_state.selected_stack:
            st.markdown(f'<span class="tag">{tool}</span>', unsafe_allow_html=True)
    else:
        st.caption("No stack selected yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="nexus-card">', unsafe_allow_html=True)
    st.subheader("Why this MVP matters")
    st.write("- It mirrors your real multi-tool handoff behavior.")
    st.write("- It lets you inspect workflow structure before paying for APIs.")
    st.write("- It creates the control layer that future live connectors will plug into.")
    st.write("- It reduces copy-paste chaos by centralizing objective, sequence, and outputs.")
    st.markdown('</div>', unsafe_allow_html=True)
