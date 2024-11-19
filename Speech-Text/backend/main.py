from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import whisper
import os

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model
model = whisper.load_model("base")

# Directory to save temporary files
TEMP_DIR = "temp"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    try:
        # Validate file type (optional, based on your requirements)
        if not audio.filename.endswith((".webm", ".wav", ".mp3")):
            return JSONResponse(
                {"error": "Unsupported audio format. Please upload a .webm, .wav, or .mp3 file."},
                status_code=400,
            )

        # Save uploaded file to a temporary directory
        temp_file_path = os.path.join(TEMP_DIR, audio.filename)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await audio.read())

        # Transcribe audio using Whisper
        result = model.transcribe(temp_file_path)
        transcription = result["text"]

        # Clean up the temporary file
        os.remove(temp_file_path)

        # Return transcription
        return JSONResponse({"transcription": transcription})

    except Exception as e:
        # Handle any errors
        return JSONResponse(
            {"error": f"An error occurred during transcription: {str(e)}"},
            status_code=500,
        )
