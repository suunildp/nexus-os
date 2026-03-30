# Configuration for Nexus OS App

# Connector Definitions with priorities
CONNECTORS = {
    'perplexity': {'name': 'Perplexity', 'icon': '🔍', 'priority': 1},
    'gemini': {'name': 'Gemini', 'icon': '✨', 'priority': 2},
    'claude': {'name': 'Claude', 'icon': '🤖', 'priority': 2},
    'chatgpt': {'name': 'ChatGPT', 'icon': '💬', 'priority': 2},
    'julius_ai': {'name': 'Julius AI', 'icon': '📊', 'priority': 3},
    'canva': {'name': 'Canva', 'icon': '🎨', 'priority': 3},
    'gamma_ai': {'name': 'Gamma AI', 'icon': '📽️', 'priority': 3},
    'aippt': {'name': 'AIPPT', 'icon': '📑', 'priority': 3},
    'notebooklm': {'name': 'NotebookLM', 'icon': '📓', 'priority': 3},
    'grok': {'name': 'Grok', 'icon': '🧠', 'priority': 2},
    'merlin': {'name': 'Merlin', 'icon': '✨', 'priority': 3},
}

# Optimization Modes
OPTIMIZATION_MODES = {
    'quality': 'Prioritize accuracy and completeness',
    'speed': 'Prioritize fast responses',
    'eco': 'Minimize token usage and reuse research',
}

# Output Format Options
OUTPUT_FORMATS = ['document', 'presentation', 'code', 'analysis', 'summary', 'visualization', 'json', 'csv']

# UI Styling Constants
UI_COLORS = {
    'primary': '#3498db',
    'secondary': '#2ecc71',
    'accent': '#e74c3c',
    'background': '#ecf0f1',
    'text': '#2c3e50',
}

# Session Configuration
SESSION_DEFAULTS = {
    'onboarded': False,
    'goal': '',
    'output_format': '',
    'optimization': 'quality',
    'selected_connectors': [],
    'research_cache': {},
    'token_count': 0,
}