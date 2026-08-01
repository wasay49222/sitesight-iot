import cv2

print("Testing camera...")
cap = cv2.VideoCapture(0)  # Just use default, no CAP_DSHOW

if not cap.isOpened():
    print("❌ Camera not found or already in use!")
    exit()

print("✅ Camera opened successfully!")
print(f"Frame width: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}")
print(f"Frame height: {cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("⚠️ Failed to grab frame")
        break
    
    cv2.imshow("Camera Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Test complete!")