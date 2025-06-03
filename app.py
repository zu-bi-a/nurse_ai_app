import os, io, re, json, datetime, base64
import streamlit as st
from openai import OpenAI
from fpdf import FPDF
from audio_recorder_streamlit import audio_recorder
import tempfile
from pathlib import Path
from fpdf import FPDF
from indic_transliteration.sanscript import transliterate as dev_trans, DEVANAGARI, IAST
from aksharamukha import transliterate as ak_trans
from utils.text_utils import json_to_pdf
from utils.audio_utils import detect_script
from streamlit_realtime_audio_recorder import audio_recorder

client = OpenAI()
MODEL = "gpt-4o-mini"  

def load_prompt(mode: str) -> str:
    file_path = "prompts/ivf_centre.txt" if mode == "ivf" else "prompts/small_hospital.txt"
    return file_path

st.set_page_config(page_title="AI Nurse", page_icon="🩺", layout="wide",)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .mode-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 2px solid transparent;
        height: 280px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .mode-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .mode-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .mode-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .mode-description {
        color: #7f8c8d;
        font-size: 1rem;
        line-height: 1.4;
        margin-bottom: 1.5rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .chat-messages {
        height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background: white;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    
    .nurse-header {
        text-align: center;
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .voice-section {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 2px solid #e9ecef;
    }
    
    .voice-instruction {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    .completion-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .pdf-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 25px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        text-decoration: none;
        display: inline-block;
        margin-top: 1rem;
    }
    
    .pdf-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        color: white;
        text-decoration: none;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom scrollbar for chat */
    .chat-messages::-webkit-scrollbar {
        width: 6px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 10px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
</style>
""", unsafe_allow_html=True)

# State initialisation
for key, default in [
    ("mode", None),
    ("info_gathered", "NO")
]:
    if key not in st.session_state:
        st.session_state[key] = default


# Landing Screen - Enhanced Design
if st.session_state.mode is None:
    st.markdown("""
    <div class="main-header">
        <h1>🩺 AI Nurse Assistant</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.9;">
            Your intelligent healthcare companion for patient intake and consultation
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #2c3e50; margin-bottom: 3rem;'>Choose Your Healthcare Service</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("""
            <div class="mode-card">
                <div>
                    <div class="mode-icon">🏥</div>
                    <div class="mode-title">General Hospital</div>
                    <div class="mode-description">
                        General medical consultations
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Select General Hospital", key="small", use_container_width=True):
                st.session_state.mode = "small"
                st.rerun()
        
        with c2:
            st.markdown("""
            <div class="mode-card">
                <div>
                    <div class="mode-icon">👶</div>
                    <div class="mode-title">IVF Clinic</div>
                    <div class="mode-description">
                        Specialized fertility consultation
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Select IVF Clinic", key="ivf", use_container_width=True):
                st.session_state.mode = "ivf"
                st.rerun()
    
    st.stop()

if "form_data" not in st.session_state:
    if st.session_state.mode == "ivf":
        st.session_state.form_data = {
            "name": None,
            "age": None,
            "region": None,
            "partner_name": None,
            "partner_age": None,
            "pregnancies": None,
            "deliveries": None,
            "miscarriages": None,
            "menstrual_cycle_regular": None,
            "last_period": None,
            "previous_treatments": None,
            "medical_history": None,
            "surgical_history": None,
            "allergies": None,
            "family_history": None,
            "lifestyle": {
                "diet": None,
                "exercise": None,
                "stress_levels": None,
                "smoking": None,
                "drinking": None
            }
        }
    if st.session_state.mode == "small":
        st.session_state.form_data = {
            "name": None,
            "age": None,
            "region": None,
            "partner_name": None,
            "partner_age": None,
            "pregnancies": None,
            "deliveries": None,
            "miscarriages": None,
            "menstrual_cycle_regular": None,
            "last_period": None,
            "previous_treatments": None,
            "medical_history": None,
            "surgical_history": None,
            "allergies": None,
            "family_history": None,
            "lifestyle": {
                "diet": None,
                "exercise": None,
                "stress_levels": None,
                "smoking": None,
                "drinking": None,
                }
        }

MODE_META = {
    "small": {
        "avatar": "assets/small_hospital_nurse.png",
        "title":  "Welcome to the hospital"
    },
    "ivf": {
        "avatar": "assets/ivf_nurse.png",
        "title":  "Welcome to the IVF Centre"
    }
}
meta = MODE_META[st.session_state.mode]
col_left, col_right = st.columns([1, 3])   

with col_left:
    if st.button("🏠 Back to Home"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Force a complete refresh by changing query params
        st.query_params.clear()
        st.query_params["refresh"] = str(datetime.datetime.now().timestamp())
        st.rerun()
    st.title(meta["title"])
    st.image(meta["avatar"], width=180)


with col_right:
    conversation_box = st.container(height=600)
    mic_box = st.container()
    audio_bytes = ""

    fname = load_prompt(st.session_state.mode)
    try:
        with open(fname , "r", encoding="utf-8") as f: 
            system_prompt = f.read()
    except FileNotFoundError:
        print("File not found:", fname)
    current_response_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_response_id" not in st.session_state:
        st.session_state.current_response_id = None
    
    user_input = ""

    with mic_box: 
        subcol1, subcol2 = st.columns([3, 1])
        with subcol1:
            st.write("\n" * 2)
            st.write("Hi, I am your nurse and I'll help you fill out your intake form. Click on the microphone to speak.")
        with subcol2:    
            # Audio recorder component
            if st.session_state.get("info_gathered", "") != "YES":
                result = audio_recorder(
                    interval=100,
                    threshold=-50,
                    silenceTimeout=200
                )
                if result:
                    if result.get('status') == 'stopped':
                        audio_data = result.get('audioData')
                        if audio_data:
                            audio_bytes = base64.b64decode(audio_data)
                            # audio_file = io.BytesIO(audio_bytes)
                        else:
                            pass
                    elif result.get('error'):
                            st.error(f"Error: {result.get('error')}")
            else:
                # Intake is already done → skip rendering the recorder
                result = None

        # Initialize session state for tracking processed audio
        if "last_processed_audio" not in st.session_state:
            st.session_state.last_processed_audio = None
        
        user_input = ""
        
        if audio_bytes and audio_bytes != st.session_state.last_processed_audio:
            try:
                with st.spinner(""):
                    # Save audio bytes to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                        tmp_file.write(audio_bytes)
                        tmp_file_path = tmp_file.name
                    
                    # Transcribe using OpenAI Whisper
                    with open(tmp_file_path, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                        )

                    # Clean up temporary file
                    os.unlink(tmp_file_path)

                    raw = transcript.text.strip()

                    if re.search(r'[\u0900-\u097F]', raw):
                        # Hindi in Devanagari → IAST
                        user_input = dev_trans(raw, DEVANAGARI, IAST)
                    elif re.search(r'[\u0600-\u06FF]', raw):
                        # Urdu/Arabic script → Latin (IAST)
                        user_input = ak_trans.process('Arabic', 'IAST', raw)
                    else:
                        # already Latin (English etc.)
                        user_input = raw
                    
                    # Mark this audio as processed
                    st.session_state.last_processed_audio = audio_bytes
                    
            except Exception as e:
                st.error(f"Error during transcription: {str(e)}")
    
    # Wrap messages in a fixed height container
    with conversation_box:
        # Display all messages in the conversation
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        if user_input:
            st.chat_message("user").markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            response = client.responses.create(
                model=MODEL,
                instructions=system_prompt,
                input=user_input,
                previous_response_id=st.session_state.current_response_id,
            )
            print(response)
            st.session_state.current_response_id = response.id
            bot_reply = response.output_text
            lang = detect_script(bot_reply)
            st.chat_message("assistant").markdown(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

    
    
    # Keep audio and other elements outside the scrollable container
    if user_input:
        # PLAY BOT MESSAGE AS AUDIO HERE
        # Choose a multilingual voice like "coral" that supports English, Hindi, and Urdu
        tmp_mp3 = Path(tempfile.gettempdir()) / "bot_reply.mp3"
        with client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice="coral",
            input=bot_reply,
        ) as response_audio:
            response_audio.stream_to_file(tmp_mp3)
        mp3_bytes = tmp_mp3.read_bytes()
        b64 = base64.b64encode(mp3_bytes).decode()
        audio_html = f"""
        <audio autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3" />
        Your browser does not support the audio element.
        </audio>
        """
        st.components.v1.html(audio_html, height=50)
        # check if conversation is done
        if "please wait for a few minutes until the doctor calls you" in bot_reply.lower():
            st.success(" Patient intake completed.")
            st.session_state.info_gathered = "YES"
            st.experimental_rerun()

        user_input = ""


if st.session_state.info_gathered=="YES":
    if st.session_state.mode=="small":
        try:
            with open("prompts/form_prompt_hospital.txt" , "r", encoding="utf-8") as f: 
                form_prompt = f.read()
        except FileNotFoundError:
            print("File not found:", fname)
    if st.session_state.mode=="ivf":
        try:
            with open("prompts/form_prompt_ivf.txt" , "r", encoding="utf-8") as f: 
                form_prompt = f.read()
        except FileNotFoundError:
            print("File not found:", fname)
    
    conversation_text = ""
    for m in st.session_state.messages:
        speaker = "Patient" if m["role"] == "user" else "Nurse"
        conversation_text += f"{speaker}: {m['content']}\n"


    form_response = client.responses.create(
        model=MODEL,
        input=[
            {
                "role": "system",
                "content": form_prompt
            },
            {
                "role": "user",
                "content": conversation_text
            }
        ],
        previous_response_id=st.session_state.current_response_id,
    )

    st.session_state.current_response_id = form_response.id
    print("JSON Generated : \n", form_response.output_text)

    form_data_raw = form_response.output_text

    clean_text = form_data_raw.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
    clean_text = clean_text.strip()

    try:
        parsed_data = json.loads(clean_text)
        print("Parsed JSON:\n", json.dumps(parsed_data, indent=2))
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
    
    pdf_bytes = json_to_pdf(parsed_data)

    patient_name = parsed_data.get("name", "patient")
    report_filename = f"{patient_name}_intake_form.pdf"

    with col_left: 
        st.download_button(
            label="📄 Download Patient Intake PDF",
            data=pdf_bytes,
            file_name=report_filename,
            mime="application/pdf"
        )