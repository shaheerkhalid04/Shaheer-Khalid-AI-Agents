"""
Personality Chatbot - a Streamlit + Groq chat app.

Users pick an AI model and a chatbot "personality" (Math Teacher, Doctor,
Travel Guide, Chef, Tech Support). Each personality strictly limits what the
bot will answer, politely refusing anything off-topic. Conversation history
is kept for the current browser session.

Run locally:
    streamlit run app.py
"""

import os

import streamlit as st
from groq import Groq

# ---------------------------------------------------------------------------
# Personalities
#
# Each entry has a short label (shown in the UI) and a system prompt that
# tells the model exactly what it may talk about and to refuse everything
# else. Keeping the prompts here in one dict makes it easy to add more.
# ---------------------------------------------------------------------------
PERSONALITIES = {
    "Math Teacher": (
        "You are a friendly, patient math teacher. You ONLY help with "
        "mathematics: arithmetic, algebra, geometry, calculus, statistics, "
        "proofs, and math concepts. Explain steps clearly. If the user asks "
        "about anything that is not math, politely refuse in one sentence and "
        "remind them you only help with math questions."
    ),
    "Doctor": (
        "You are a knowledgeable, careful medical assistant. You ONLY answer "
        "general health, symptom, and medicine questions, and you always add "
        "a short reminder to consult a real doctor for diagnosis. If the user "
        "asks about anything that is not health or medicine, politely refuse "
        "in one sentence and remind them you only answer medical questions."
    ),
    "Travel Guide": (
        "You are an enthusiastic travel guide. You ONLY answer questions about "
        "travel: destinations, itineraries, local tips, transport, budgeting, "
        "and planning. If the user asks about anything that is not travel, "
        "politely refuse in one sentence and remind them you only give travel "
        "advice."
    ),
    "Chef": (
        "You are a warm, skilled chef. You ONLY answer questions about cooking: "
        "recipes, ingredients, techniques, substitutions, and food pairings. "
        "If the user asks about anything that is not cooking or food, politely "
        "refuse in one sentence and remind them you only answer cooking "
        "questions."
    ),
    "Tech Support": (
        "You are a calm, methodical tech support agent. You ONLY answer "
        "technical troubleshooting questions about devices, software, networks, "
        "and hardware. Give clear step-by-step fixes. If the user asks about "
        "anything that is not tech support, politely refuse in one sentence and "
        "remind them you only handle tech troubleshooting."
    ),
}

# If we cannot reach Groq to list models, fall back to these known-good ids.
# gpt-oss models are the safe current picks; the Llama ids are kept as extra
# options in case they are still enabled on the account.
FALLBACK_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]


def get_api_key():
    """
    Find the Groq API key without asking the user.

    Looks in Streamlit secrets first (set in the Streamlit Cloud dashboard
    under Settings -> Secrets, or in a local .streamlit/secrets.toml file),
    then in a GROQ_API_KEY environment variable. Returns "" only if neither
    is set, in which case the sidebar shows a key box as a fallback.
    """
    try:
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        # st.secrets raises if no secrets are configured at all; ignore it
        # and fall through to the environment variable.
        pass
    return os.environ.get("GROQ_API_KEY", "")


@st.cache_data(show_spinner=False)
def list_models(api_key):
    """
    Ask Groq which models the account can use, newest-friendly first.

    Returns a list of chat-capable model ids. Cached so we don't call the
    API on every rerun. Falls back to FALLBACK_MODELS on any error.
    """
    try:
        client = Groq(api_key=api_key)
        models = client.models.list().data
        # Keep only text/chat models: drop audio (whisper/tts/orpheus) and
        # safety guard models, which can't hold a normal conversation.
        skip = ("whisper", "tts", "guard", "orpheus")
        ids = [
            m.id
            for m in models
            if not any(word in m.id.lower() for word in skip)
        ]
        ids.sort()
        return ids or FALLBACK_MODELS
    except Exception:
        return FALLBACK_MODELS


def build_messages(system_prompt, history):
    """Combine the personality's system prompt with the chat history."""
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    return messages


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Personality Chatbot",
    page_icon="💬",
    initial_sidebar_state="expanded",
)
st.title("💬 Personality Chatbot")
st.caption("Powered by Groq. Pick a model and a personality, then start chatting.")

api_key = get_api_key()

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Settings")

    if not api_key:
        api_key = st.text_input(
            "Groq API key",
            type="password",
            help="Get a free key at https://console.groq.com/keys",
        )

    if api_key:
        model_options = list_models(api_key)
    else:
        model_options = FALLBACK_MODELS

    model = st.selectbox("Model", model_options)
    personality = st.selectbox("Personality", list(PERSONALITIES.keys()))

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.caption(
        "Each personality only answers questions in its area and politely "
        "refuses anything else."
    )

# ---------------------------------------------------------------------------
# Chat state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the conversation so far.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------------------------------------------------------------------
# Handle a new user message
# ---------------------------------------------------------------------------
prompt = st.chat_input("Type your message...")

if prompt:
    if not api_key:
        st.error("Please enter your Groq API key in the sidebar first.")
        st.stop()

    # Show and store the user's message.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ask the model, streaming the reply so it appears as it is written.
    system_prompt = PERSONALITIES[personality]
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=api_key)
            stream = client.chat.completions.create(
                model=model,
                messages=build_messages(system_prompt, st.session_state.messages),
                stream=True,
            )

            def token_stream():
                for chunk in stream:
                    text = chunk.choices[0].delta.content
                    if text:
                        yield text

            reply = st.write_stream(token_stream())
        except Exception as error:
            reply = "Sorry, something went wrong: " + str(error)
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
