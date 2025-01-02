# main.py

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import cv2
from src.api.camera import Camera

app = FastAPI()
templates = Jinja2Templates(directory="templates")

camera = Camera(video_source=0)

def generate_frames():
    while True:
        ret, frame = camera.get_frame()
        if not ret:
            continue
        # Mã hóa khung hình thành JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame_bytes = buffer.tobytes()
        # Định dạng theo chuẩn multipart
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Trang chủ hiển thị video từ webcam
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video_feed")
async def video_feed():
    """
    Endpoint phát trực tiếp video từ webcam
    """
    return StreamingResponse(generate_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")
