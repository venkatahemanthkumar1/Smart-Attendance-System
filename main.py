import serial
import face_recognition
import cv2
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ==============================
# SERIAL SETUP
# ==============================
ser = serial.Serial('COM13', 115200, timeout=1)

# ==============================
# LOAD KNOWN FACES (Supports multiple images per person)
# ==============================
known_encodings = []
known_names = []

for file in os.listdir("known_faces"):
    image = face_recognition.load_image_file(f"known_faces/{file}")
    encodings = face_recognition.face_encodings(image)

    if len(encodings) > 0:
        known_encodings.append(encodings[0])

        # Remove numbers from filename (hemanth1 → hemanth)
        name = os.path.splitext(file)[0]
        name = ''.join([i for i in name if not i.isdigit()])
        known_names.append(name)

print("Known faces loaded.")

# ==============================
# ATTENDANCE FILE
# ==============================
attendance_file = "attendance.xlsx"

if not os.path.exists(attendance_file):
    df = pd.DataFrame(columns=["Name", "Date", "Time"])
    df.to_excel(attendance_file, index=False)

# ==============================
# CAMERA SETUP
# ==============================
video = cv2.VideoCapture(0)
print("Camera opened. System running for 10 minutes...")

display_name = "No Scan Yet"
display_status = "Waiting..."

# ==============================
# MARK ATTENDANCE FUNCTION
# ==============================
def mark_attendance(name):
    global display_name, display_status

    df = pd.read_excel(attendance_file)
    today = datetime.now().strftime("%Y-%m-%d")

    if ((df["Name"] == name) & (df["Date"] == today)).any():
        display_name = name
        display_status = "Already Marked Today"
        print("Already marked.")
        return

    time_now = datetime.now().strftime("%H:%M:%S")
    new_row = {"Name": name, "Date": today, "Time": time_now}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_excel(attendance_file, index=False)

    display_name = name
    display_status = "Attendance Marked Successfully"
    print("Attendance marked.")

# ==============================
# MAIN LOOP
# ==============================
end_time = datetime.now() + timedelta(minutes=10)

while datetime.now() < end_time:

    ret, frame = video.read()
    if not ret:
        continue

    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = small_frame[:, :, ::-1]

    if ser.in_waiting > 0:
        rfid_name = ser.readline().decode().strip().lower()
        print("RFID:", rfid_name)

        if rfid_name == "unknown_card":
            display_name = "Unknown"
            display_status = "Unknown RFID Card"
        else:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_name = "Unknown"

            for encoding in face_encodings:

                face_distances = face_recognition.face_distance(known_encodings, encoding)

                if len(face_distances) > 0:

                    best_match_index = np.argmin(face_distances)
                    best_distance = face_distances[best_match_index]
                    best_name = known_names[best_match_index]

                    print("Best match:", best_name)
                    print("Distance:", best_distance)

                    # STRICT THRESHOLD (very important)
                    if best_distance < 0.60:
                        face_name = best_name.lower()
                    else:
                        face_name = "unknown"

            print("Detected:", face_name)

            if rfid_name == face_name:
                mark_attendance(face_name)
            else:
                display_name = face_name
                display_status = "RFID and Face Do Not Match"

    # DISPLAY PANEL
    cv2.rectangle(frame, (10, 10), (700, 120), (0, 0, 0), -1)

    cv2.putText(frame, f"Name: {display_name}",
                (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2)

    cv2.putText(frame, f"Status: {display_status}",
                (20, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 255),
                2)

    cv2.imshow("Attendance Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
ser.close()

print("System finished.")