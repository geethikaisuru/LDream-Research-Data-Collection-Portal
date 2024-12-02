import streamlit as st
from st_audiorec import st_audiorec
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import os
import wave
import numpy as np

# Page title and set wide mode
st.set_page_config(page_title="Dream Research Form", page_icon="🌌", layout = "wide")

# Use Google Cloud credentials from secrets.toml
def init_google_services():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["connections"],
            scopes=[
                "https://www.googleapis.com/auth/drive.file",
                "https://www.googleapis.com/auth/spreadsheets"
            ]
        )
        drive_service = build("drive", "v3", credentials=credentials)
        sheets_service = build("sheets", "v4", credentials=credentials)
        return drive_service, sheets_service
    except Exception as e:
        st.error(f"Error initializing Google APIs: {e}")
        return None, None

# Upload a file to Google Drive
def upload_to_drive(drive_service, file_path, filename, mime_type):
    file_metadata = {"name": filename, "parents": [st.secrets["DRIVE_FOLDER_ID"]]}
    media = MediaFileUpload(file_path, mimetype=mime_type)
    try:
        drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        st.success(f"{filename} recording is successfully uploaded. Thank you 🙏")
    except Exception as e:
        st.error(f"Failed to upload {filename}. Error: {e}")

# Save WAV data to a file
def save_wav_file(audio_data, filename):
    # Convert the byte data from st_audiorec to a NumPy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)               # Mono channel
        wf.setsampwidth(2)               # 16-bit (2 bytes per sample)
        wf.setframerate(44100)           # Set the sampling rate to 44100 Hz
        wf.writeframes(audio_array.tobytes())

# Append text data to Google Sheet
def append_to_google_sheet(sheets_service, text):
    try:
        body = {"values": [[text]]}
        sheets_service.spreadsheets().values().append(
            spreadsheetId=st.secrets["SHEET_ID"],
            range=f"{st.secrets['SHEET_NAME']}!A:A",
            valueInputOption="RAW",
            body=body
        ).execute()
        st.success("Dream Text submission successfully added. Thank you 🙏")
    except Exception as e:
        st.error(f"Failed to append your dream. Error: {e}")

# Streamlit app
def main():
    st.title("Lucid Dreams Research ✨🌌💫")
    st.write("Please submit your lucid dream by recording a voice message or writing text below.")

    # Initialize Google APIs
    drive_service, sheets_service = init_google_services()
    if drive_service is None or sheets_service is None:
        return

    # Form for audio or text submission
    with st.form("submission_form"):
        #audio_data = st_audiorec()
        audio_data = None
        try:
            audio_data = st_audiorec()
        except Exception as e:
            st.error(f"Error recording audio: {e}. Please check microphone permissions and try again.")
        
        text_input = st.text_area("Or write your dream here:", "")
        submit_button = st.form_submit_button("Submit")

    # Handle submission
    if submit_button:
        if audio_data:
            st.audio(audio_data, format="audio/wav")
            audio_filename = "audio_submission.wav"
            save_wav_file(audio_data, audio_filename)
            upload_to_drive(drive_service, audio_filename, audio_filename, "audio/wav")
            os.remove(audio_filename)
        elif text_input.strip():
            append_to_google_sheet(sheets_service, text_input.strip())
        else:
            st.error("Please submit either a voice recording or a text.💭")

    st.write("Thank you so much! We will use your anonymous data to help us with our research.🛡️")
    st.write("This research is conducted by Buhuni, a 2nd year student at the University of Sri Jayewardenepura")
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write("Portal Developed with ❤️ by [Geethika.](https://www.linkedin.com/in/geethikaisuru/)")

if __name__ == "__main__":
    main()
