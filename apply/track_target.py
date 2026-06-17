import cv2
import numpy as np #简化

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([100, 100, 0])
    upper_red1 = np.array([140, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255]) #红色范围，什么样的像素算是红色

    mask = cv2.inRange(hsv, lower_red1, upper_red1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = 0
    best_contour = None

    #  找最大轮廓
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_area and area > 500:
            max_area = area
            best_contour = cnt

    #  只处理最大目标
    if best_contour is not None:
        x, y, w, h = cv2.boundingRect(best_contour)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cx = x + w // 2
        cy = y + h // 2

        cv2.circle(frame, (cx, cy), 5, (255, 0, 0), -1)

        print(f"锁定目标: ({cx}, {cy})")

    cv2.imshow("tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()