# AI-Agent 🤖

AI-Agent is an intelligent assistant that integrates with Groq LLMs and custom functions to provide a multifunctional AI experience. It can perform natural language search, retrieve real-time weather reports, search files or folders on your local system, send emails, and perform Retrieval-Augmented Generation (RAG) analysis on various document formats.

---

## Features

- **General AI (LLM) Search:** Ask anything and get answers powered by large language models.
- **Real-time Weather Reports:** Get the current weather for any place in the world.
- **File/Folder Search:** Search for files or folders in your local system.
- **Write and Send Emails:** Compose and send emails directly from the agent using your Gmail account.
- **RAG Analysis:** Analyze and extract information from `.pdf`, `.txt`, and `.doc` files.

---

## Getting Started

Follow these steps to set up and use the AI-Agent:

### 1. Get Your Groq API Key

- Sign up or log in to [Groq](https://groq.com/) to obtain your API key.
- Copy your API key for later use.

### 2. Generate a Google Account App Password

To allow the agent to send emails via your Gmail, you need to generate an App Password:

- Ensure 2-Step Verification is enabled on your Google Account.
- Visit [Google App Passwords](https://myaccount.google.com/apppasswords).
- Generate a new app password for "Mail" and "Windows Computer" (or any device).
- Save the generated password securely.

### 3. Install Necessary Dependencies

Make sure you have Python installed (version 3.8+ is recommended).

Install dependencies using pip:

```bash
pip install -r requirements.txt
```

Or, if you use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure Your Environment

Create a `.env` file in the project’s root directory and add your credentials:

```
GROQ_API_KEY=your_groq_api_key
GOOGLE_APP_PASSWORD=your_google_app_password
GMAIL_ADDRESS=your_gmail_address
```

### 5. Talk with Your Agent

Start the AI-Agent using:

```bash
python main.py
```

(Adjust the entry point if your main script has a different name.)

---

## Notes

- **Inaccuracy Warning:** Sometimes, the answers provided by the AI may be inaccurate. Use critical thinking and verify important information.
- **Performance:** File and folder search operations may take some time depending on the size and structure of your local file system.

---

## License

[MIT](LICENSE)

---

## Acknowledgements

- [Groq](https://groq.com/)
- [Google](https://google.com/)
