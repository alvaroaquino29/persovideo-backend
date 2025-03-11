from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import os
import subprocess
import firebase_admin
from firebase_admin import credentials, storage
import uuid

app = FastAPI()

# Inicialize o Firebase
cred = credentials.Certificate("caminho/para/suas/credenciais-firebase.json")
firebase_admin.initialize_app(cred, {"storageBucket": "seu-bucket-firebase.appspot.com"})

@app.post("/process_video")
async def process_video(video: UploadFile, name: str = Form(...)):
    # Salve o vídeo recebido
    video_path = f"{uuid.uuid4()}.mp4"
    with open(video_path, "wb") as buffer:
        buffer.write(await video.read())

    # Processar o vídeo com FFmpeg
    output_path = f"{uuid.uuid4()}_processed.mp4"
    subprocess.run(["ffmpeg", "-i", video_path, "-vf", f"drawtext=text='{name}':x=10:y=10:fontsize=50:fontcolor=white", output_path])

    # Envie o vídeo processado para o Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(output_path)
    blob.upload_from_filename(output_path)
    blob.make_public()

    # Retorne a URL pública do vídeo
    download_url = blob.public_url

    # Remova os arquivos locais
    os.remove(video_path)
    os.remove(output_path)

    return {"download_url": download_url}