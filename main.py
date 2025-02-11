from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import shutil
from pathlib import Path
import uuid
import asyncio 

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  
)

SAVE_ROOT = Path("./public/videos")  
RESULTS_ROOT = Path("./results")

os.makedirs(SAVE_ROOT, exist_ok=True)
os.makedirs(RESULTS_ROOT, exist_ok=True)

from fastapi.responses import FileResponse

@app.post("/generate-video/")
async def generate_video(file: UploadFile = File(...)):
    try:
        user_id = str(uuid.uuid4())[:8]
        audio_path = SAVE_ROOT / f"{user_id}.wav"

        with open(audio_path, "wb") as buffer:
            buffer.write(await file.read())

        result_dir = RESULTS_ROOT / user_id
        result_dir.mkdir(parents=True, exist_ok=True)

        subprocess.call([
            "python", "video.py", "--id", "May",
            "--driving_audio", str(audio_path), "--device", "cuda"
        ])

        avi_video_path = RESULTS_ROOT / user_id / f"{user_id}.avi"
        mp4_video_path = SAVE_ROOT / f"{user_id}.mp4"

        await asyncio.sleep(1)

        if avi_video_path.exists():
            ffmpeg_command = [
                "ffmpeg", "-i", str(avi_video_path),
                "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-movflags", "+faststart", str(mp4_video_path)
            ]
            subprocess.run(ffmpeg_command, check=True)

            print(f"✅ Final video saved at: {mp4_video_path}")

            return FileResponse(
                path=mp4_video_path,
                filename=f"{user_id}.mp4",
                media_type="video/mp4",
                headers={"Content-Disposition": f"inline; filename={user_id}.mp4"}
            )
        else:
            return JSONResponse(content={"error": "Video generation failed, AVI file not found."}, status_code=500)

    except subprocess.CalledProcessError as e:
        return JSONResponse(content={"error": f"FFmpeg failed: {str(e)}"}, status_code=500)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
