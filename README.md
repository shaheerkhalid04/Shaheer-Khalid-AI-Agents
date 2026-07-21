# Personality Chatbot (Streamlit + Groq)

An interactive chatbot web app. Users chat in real time, pick which Groq AI
model to use, and choose a chatbot **personality** (Math Teacher, Doctor,
Travel Guide, Chef, Tech Support). Each personality strictly limits what the
bot answers and politely refuses anything off-topic. Conversation history is
kept for the current session.

## Features

- **Chat interface** built with Streamlit's chat components.
- **Model selection** from the models your Groq account can use (fetched live,
  so it never breaks when Groq retires a model).
- **Five personalities**, each with a system prompt that keeps the bot on topic.
- **Personality enforcement**: off-topic questions get a polite refusal.
- **Session memory**: the bot remembers the current conversation.
- **Streaming replies** that appear as they are written.

## Run locally

1. Install the requirements:

   ```
   pip install -r requirements.txt
   ```

2. Get a free Groq API key at <https://console.groq.com/keys>.

3. Provide the key one of two ways:

   - Paste it into the sidebar when the app opens, **or**
   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and
     put your key there.

4. Start the app:

   ```
   streamlit run app.py
   ```

## Deploy free on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to <https://share.streamlit.io>, sign in with GitHub, and click
   **New app**.
3. Pick this repository, branch `main`, and `app.py` as the entry point.
4. Under **Advanced settings -> Secrets**, add:

   ```
   GROQ_API_KEY = "your_groq_key_here"
   ```

5. Click **Deploy**. Streamlit gives you a public URL to share.

## Personalities

| Personality  | Answers only about                         |
| ------------ | ------------------------------------------ |
| Math Teacher | Math problems and concepts                 |
| Doctor       | Health, symptoms, medicine                 |
| Travel Guide | Destinations, tips, trip planning          |
| Chef         | Cooking, recipes, ingredients              |
| Tech Support | Devices, software, troubleshooting         |
