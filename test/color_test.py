import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 转HSV（重点）
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 红色范围（第一段）
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])

    # 红色范围（第二段）
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask = mask1 + mask2

    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("original", frame)
    cv2.imshow("mask", mask)
    cv2.imshow("result", result)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()