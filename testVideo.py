import cv2
import base64
import time
import httpx
import asyncio

# Mở kết nối với webcam (chỉ số video source là 0)
cap = cv2.VideoCapture("http://localhost:8000/export_camera")  # URL của stream camera

# Kiểm tra kết nối
if not cap.isOpened():
    print("Không thể kết nối với webcam.")
    exit()

# Thiết lập thời gian ban đầu để chờ 3 giây
last_processed_time = time.time()

async def send_frame_to_api(frame):
    """Gửi frame đã mã hóa tới API thứ 2."""
    _, buffer = cv2.imencode('.jpg', frame)  # Mã hóa frame thành JPEG
    img_buffer = buffer.tobytes()

    # Mã hóa frame thành base64 để gửi qua HTTP
    payload = {
        "frame": base64.b64encode(img_buffer).decode("utf-8")
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://localhost:8005/process-frame", json=payload)
            print(f"Processed frame: {response.json()}")
    except Exception as e:
        print(f"Error sending frame to API: {e}")

async def read_and_process_frames():
    """
    Đọc video stream từ webcam và gửi 1 frame mỗi 3 giây tới API thứ 2 để xử lý.
    """
    frame_count = 0
    print("call1")

    while True:
        ret, frame = cap.read()  # Lấy frame từ camera (webcam)
        if not ret or frame is None:
            print("Error: Couldn't get frame from camera.")
            continue

        # Mỗi 3 giây lấy 1 frame
        timestamp = int(time.time())
        if timestamp % 3 == 0:  # Mỗi 3 giây
            cv2.imshow("RTSP Stream", frame)  # Hiển thị frame trong cửa sổ
            _, buffer = cv2.imencode('.jpg', frame)  # Mã hóa khung hình thành JPEG
            img_buffer = buffer.tobytes()
            print("call2")
            # Gửi frame tới API thứ 2 để xử lý
            payload = {
                "frame": base64.b64encode(img_buffer).decode("utf-8")
            }
            print("Sending frame after 3 seconds")

            try:
                # Gọi API thứ 2 để xử lý frame
                async with httpx.AsyncClient() as client:
                    response = await client.post("http://localhost:8001/process-frame", json=payload)
                    print(f"Processed frame: {response.json()}")
            except httpx.ReadTimeout as timeout_error:
                print(f"Timeout error: {timeout_error}. Skipping this frame.")
            except Exception as e:
                print(f"Error sending frame to API: {e}")

            await asyncio.sleep(3)  # Chờ 3 giây trước khi lấy frame tiếp theo

        # Đảm bảo OpenCV xử lý sự kiện
        cv2.waitKey(1)  # Đợi để xử lý sự kiện của cửa sổ

# Chạy async function trong event loop
async def main():
    await read_and_process_frames()

# Chạy chương trình
if __name__ == "__main__":
    asyncio.run(main())

# Giải phóng tài nguyên khi thoát chương trình
cap.release()
cv2.destroyAllWindows()
