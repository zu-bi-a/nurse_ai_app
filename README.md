# AI Nurse Assistant (Streamlit)

A simple Streamlit-based voice AI nurse application that guides patient intake (general hospital or IVF clinic), transcribes user speech via OpenAI Whisper, responds via GPT, and generates a PDF intake form.

## Features

- **Landing Page**: Choose between “General Hospital” or “IVF Clinic” modes.
- **Voice Input**: Click a microphone icon to record patient speech. Whisper transcribes Hindi, Urdu, or English into text.
- **AI Chat**: GPT-4o-mini handles follow-up questions and replies in real time.
- **Transcript Box**: Scrollable, fixed-height panel that shows all “Patient:” and “Nurse:” messages.
- **PDF Output**: When intake is complete, the app generates a PDF summary of the conversation and opens it in a new tab.

## Prerequisites

- Python 3.8 or newer
- An OpenAI API key with access to Whisper and GPT-4o-mini
- A modern web browser

## Local Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/ai-nurse-assistant.git
   cd ai-nurse-assistant
   ```

2. **Create a virtual environment** (recommended)  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate       # macOS/Linux
   .venv\Scripts\activate        # Windows
   ```

3. **Install dependencies**  
   If there’s a `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
   ```
   Otherwise install manually:
   ```bash
   pip install streamlit openai python-dotenv fpdf audio-recorder-streamlit gtts indic-transliteration aksharamukha
   ```

4. **Create a `.env` file** in the project root and add your OpenAI API key:  
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Verify folder structure**  
   Make sure you have:
   - `assets/` containing `small_hospital_nurse.png` and `ivf_nurse.png`
   - `prompts/` containing the four `.txt` prompt files
   - `utils/text_utils.py` and `utils/audio_utils.py` present

## Running the App

From the project root, run:

```bash
streamlit run app.py
```

- The landing page will open in your default browser (`http://localhost:8501` by default).
- Select **General Hospital** or **IVF Clinic** to begin.
- Click the microphone icon in the middle column to record patient speech.
- Once the intake conversation ends (“please wait for a few minutes…”), a link appears to open the PDF in a new tab.

## Troubleshooting

- **“ModuleNotFoundError”**: Make sure you installed all required packages and that your virtual environment is activated.
- **Prompt files not found**: Confirm `prompts/` contains the correct `.txt` files.
- **No audio recorder**: Confirm `audio-recorder-streamlit` is installed (`pip install audio-recorder-streamlit`) and that your browser allows microphone access.

---

That’s it! You should now have a working local instance of the AI Nurse Assistant. Feel free to customize prompts, styles, or avatars as needed.