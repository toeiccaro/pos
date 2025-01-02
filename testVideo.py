import cv2

# Mở kết nối với RTSP stream
cap = cv2.VideoCapture("http://localhost:8000/export_camera")

# Kiểm tra kết nối
if not cap.isOpened():
    print("Không thể kết nối với RTSP stream.")
    exit()

# Hiển thị video trong cửa sổ
while True:
    ret, frame = cap.read()
    if not ret:
        print("Không thể đọc frame từ RTSP.")
        break

    # Hiển thị khung hình
    cv2.imshow("RTSP Stream", frame)

    # Nếu nhấn 'q', thoát khỏi vòng lặp
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
