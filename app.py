import streamlit as st

# Function to handle onboarding

def onboarding():
    st.header("Welcome to Nexus OS")
    st.subheader("Let's get started with onboarding.")
    goal = st.text_input("What is your goal for using Nexus OS?")
    output_format = st.selectbox("Select your desired output format:", ["JSON", "XML", "Text"])
    optimization_pref = st.selectbox("Select your optimization preference:", ["Speed", "Accuracy", "Cost"])
    allowed_connectors = st.multiselect("Select allowed connectors:", ["Perplexity", "Gemini", "Claude", "ChatGPT", "Julius AI", "Canva", "Gamma AI", "AIPPT", "NotebookLM", "Grok", "Merlin"])
    if st.button("Confirm"): 
        st.success("Onboarding completed!\n\n" + 
                f"Goal: {goal}\n" + 
                f"Output Format: {output_format}\n" + 
                f"Optimization Preference: {optimization_pref}\n" + 
                f"Allowed Connectors: {', '.join(allowed_connectors)}")

# Main function of the Streamlit app

def main():
    st.set_page_config(page_title="Nexus OS", layout="wide")
    if 'onboarded' not in st.session_state:
        st.session_state['onboarded'] = False

    if not st.session_state['onboarded']:
        onboarding() 
        st.session_state['onboarded'] = True
    else:
        st.write("Welcome back to Nexus OS!")

if __name__ == '__main__':
    main()