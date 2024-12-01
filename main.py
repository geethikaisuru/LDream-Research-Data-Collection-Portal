import streamlit as st
from st_audiorec import st_audiorec
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import pandas as pd
import os
import wave

# Google Drive folder ID
DRIVE_FOLDER_ID = "11CwkY3WVRlnOZWgGfHFBRH5RrCPyqed0"
CSV_FILENAME = "dream_submissions.csv"

# Initialize Google Drive API
def init_google_drive():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            "credentials.json",
            scopes=["https://www.googleapis.com/auth/drive.file"]
        )
        return build("drive", "v3", credentials=credentials)
    except Exception as e:
        st.error(f"Error initializing Google Drive API: {e}")
        return None

# Upload a file to Google Drive
def upload_to_drive(drive_service, file_path, filename, mime_type):
    file_metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(file_path, mimetype=mime_type)
    try:
        drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        st.success(f"{filename} successfully uploaded to Google Drive.")
    except Exception as e:
        st.error(f"Failed to upload {filename}. Error: {e}")

# Save WAV data to a file
def save_wav_file(audio_data, filename):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(44100)
        wf.writeframes(audio_data)

# Append text data to a CSV file
def append_to_csv(text, csv_filename):
    new_entry = pd.DataFrame({"Text Submission": [text]})  # Create a new DataFrame for the entry
    if not os.path.exists(csv_filename):
        # Create the file with headers if it doesn't exist
        new_entry.to_csv(csv_filename, index=False)
    else:
        # Read the existing CSV and append the new entry
        existing_data = pd.read_csv(csv_filename)
        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
        updated_data.to_csv(csv_filename, index=False)

# Streamlit app
def main():
    st.title("Dream Research Form")
    st.write("Please submit your dream by recording a voice message or writing text below.")

    # Initialize Google Drive API
    drive_service = init_google_drive()
    if drive_service is None:
        return

    # Form for audio or text submission
    with st.form("submission_form"):
        audio_data = st_audiorec()
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
            append_to_csv(text_input, CSV_FILENAME)
            upload_to_drive(drive_service, CSV_FILENAME, CSV_FILENAME, "text/csv")
        else:
            st.error("Please submit either a voice recording or a text.")

if __name__ == "__main__":
    main()
