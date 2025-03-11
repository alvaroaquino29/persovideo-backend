from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse
import os
import subprocess
import uuid
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

app = FastAPI()

# Autenticação do Google Drive
gauth = GoogleAuth()
gauth.LocalWebserverAuth()  # Cria as credenciais se necessário
drive = GoogleDrive(gauth)

@app.post("/process_video")
async def process_video(video: UploadFile, name: str = Form(...)):
    # Salve o vídeo recebido
    video_path = f"{uuid.uuid4()}.mp4"
    with open(video_path, "wb") as buffer:
        buffer.write(await video.read())

    # Processar o vídeo com FFmpeg
    output_path = f"{uuid.uuid4()}_processed.mp4"
    subprocess.run(["ffmpeg", "-i", video_path, "-vf", f"drawtext=text='{name}':x=10:y=10:fontsize=50:fontcolor=white", output_path])

    # Envie o vídeo processado para o Google Drive
    file_drive = drive.CreateFile({'title': output_path})
    file_drive.SetContentFile(output_path)
    file_drive.Upload()

    # Gere o link de download do Google Drive
    download_url = file_drive['alternateLink']

    # Remova os arquivos locais
    os.remove(video_path)
    os.remove(output_path)

    return {"download_url": download_url}