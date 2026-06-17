import cv2
import numpy as np
import platform

def open_camera(index=0):
    backends = [None]
    if platform.system() == "Windows":
        backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]

    for backend in backends:
        cap = cv2.VideoCapture(index) if backend is None else cv2.VideoCapture(index, backend)
        if cap.isOpened():
            return cap
        cap.release()

    return None


cap = open_camera(0)
if cap is None:
    print("无法打开摄像头，请检查设备占用，或尝试更换摄像头编号/后端")
    raise SystemExit(1)

cx_old = 0
cy_old = 0

# 丢失计时器
lost_count = 0
max_lost = 10

# 平滑与控制参数（可调整）
alpha = 0.7
k = 0.1
threshold = 20

# UI显示函数
def draw_ui(frame, state, dx, dy, speed_x, speed_y):
    x1, y1, w, h = 10, 10, 185, 75
    x2, y2 = x1 + w, y1 + h

    # 半透明深色背景
    roi = frame[y1:y2, x1:x2]
    bg = np.full_like(roi, (30, 30, 30))
    blended = cv2.addWeighted(bg, 0.6, roi, 0.4, 0)
    frame[y1:y2, x1:x2] = blended

    # 细边框
    cv2.rectangle(frame, (x1, y1), (x2, y2), (80, 80, 80), 1)

    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.4
    green = (0, 200, 0)
    white = (220, 220, 220)

    cv2.putText(frame, f"STATE: {state}", (16, 24), font, scale, green, 1, cv2.LINE_AA)
    cv2.putText(frame, f"dx: {dx}",        (16, 45), font, scale, white, 1, cv2.LINE_AA)
    cv2.putText(frame, f"dy: {dy}",        (100, 45), font, scale, white, 1, cv2.LINE_AA)
    cv2.putText(frame, f"sx: {speed_x:.2f}", (16, 66), font, scale, white, 1, cv2.LINE_AA)
    cv2.putText(frame, f"sy: {speed_y:.2f}", (100, 66), font, scale, white, 1, cv2.LINE_AA)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width = frame.shape[:2]

    # 画面中心
    center_x = width // 2
    center_y = height // 2

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    state = "lost"
    dx = 0
    dy = 0
    speed_x = 0
    speed_y = 0
    x = y = w = h = 0
    max_area = 0
    best_contour = None

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area and area > 500:
            max_area = area
            best_contour = cnt

    # 画中心点
    cv2.circle(frame, (center_x, center_y), 5, (0, 0, 255), -1)

    if best_contour is not None:
        state = "lock"
        x, y, w, h = cv2.boundingRect(best_contour)

        cx = x + w // 2
        cy = y + h // 2
        cx_old, cy_old = cx, cy
        lost_count = 0
    else:
        state = "lost"
        cx,cy=cx_old, cy_old
        lost_count += 1

        if lost_count > max_lost:
            cx_old, cy_old = center_x, center_y
            cx, cy = center_x, center_y

    # 计算偏差（平滑）
    cx = int(alpha * cx_old + (1 - alpha) * cx)
    cy = int(alpha * cy_old + (1 - alpha) * cy)

    dx = cx - center_x
    dy = cy - center_y

    # 画目标
    if state == "lock":
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

    # 比例控制（P控制）
    if abs(dx) < threshold:
        speed_x = 0
    else:
        speed_x = dx * k

    if abs(dy) < threshold:
        speed_y = 0
    else:
        speed_y = dy * k

    if abs(dx) < threshold and abs(dy) < threshold:
        print("🎯 已对准")
    else:
        if dx > threshold:
            print("➡ 向右转")
        elif dx < -threshold:
            print("⬅ 向左转")

        if dy > threshold:
            print("⬇ 向下转")
        elif dy < -threshold:
            print("⬆ 向上转")

    draw_ui(frame, state, dx, dy, speed_x, speed_y)
    cv2.imshow("aim", frame)
    

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()