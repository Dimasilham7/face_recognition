import cv2
import face_recognition
from PIL import Image, ImageDraw, ImageFont
import datetime
import sqlite3
import os
import numpy as np
import dlib
import uuid

# Path to the folder containing the images
folder_path = 'ID/'

# RTSP stream URL or MP4 file path
video_source = 'video/PXL_20240317_190355288.TS.mp4'

# Connect to the SQLite database
conn = sqlite3.connect('company.db')
cursor = conn.cursor()

# Load the list of images
list_of_images = os.listdir(folder_path)

# Initialize lists to store face encodings and names
list_of_face_encoding = []
known_face_names = []
check_in_times = {}  # Dictionary to store check-in times
check_out_times = {}  # Dictionary to store check-out times

# Create the output directory if it doesn't exist
output_directory = 'output_data'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Iterate over each image in the folder
for image_name in list_of_images:
    image_path = os.path.join(folder_path, image_name)
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]

    # Append the encoding and name to the lists
    list_of_face_encoding.append(encoding)
    known_face_names.append(os.path.splitext(image_name)[0])
    check_in_times[os.path.splitext(image_name)[0]] = None  # Initialize check-in time as None
    check_out_times[os.path.splitext(image_name)[0]] = None  # Initialize check-out time as None

# Load the video capture
cap = cv2.VideoCapture(video_source)

# Initialize dlib's face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Initialize variables for font settings
font_path = 'msyhbd.ttf'
font_size = 13

# Define EAR threshold and consecutive frames for blink detection
EAR_THRESHOLD = 0.25
CONSEC_FRAMES = 3
blink_counter = 0
fatigue_detected = False

def calculate_ear(eye):
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    C = np.linalg.norm(eye[0] - eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def register_new_user(frame_rgb):
    # Prompt the user to input their name
    name = input("New person detected. Please enter your name: ")

    # Convert the frame to BGR (required by cv2.imwrite)
    frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    # Save the frame as an image with the person's name
    image_path = f'ID/{name}.png'
    cv2.imwrite(image_path, frame_bgr)
    print(f"Image saved for {name}: {image_path}")

    print(f"Welcome, {name}! You've been registered. already save in database!")




# Read video frames
while True:
    ret, frame = cap.read()
    if not ret:
        break  # Exit if there are no more frames
    
    # Convert the frame to RGB (required by face_recognition library)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect face locations and encodings
    face_locations = face_recognition.face_locations(frame_rgb)
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)

    # Convert the frame to PIL format
    pil_image = Image.fromarray(frame_rgb)

    # Draw on the frame
    draw = ImageDraw.Draw(pil_image)

    # Iterate over each face in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(list_of_face_encoding, face_encoding)

        detected_name = "Unknown Person"

        if True in matches:
            first_match_index = matches.index(True)
            detected_name = known_face_names[first_match_index]

        if detected_name == "Unknown Person":
            register_new_user(frame_rgb)
            pass  # Skip processing for unknown persons


        # Get the name and company from the detected name
        name_with_company = detected_name
        name, company = name_with_company.split(" - ") if " - " in name_with_company else (name_with_company, "")

        # Retrieve check-in time from the dictionary
        check_in_time = check_in_times.get(name_with_company, None)

        # Retrieve employee information from the database
        cursor.execute("SELECT employee_id, department FROM employees WHERE name = ?", (name,))
        employee_info = cursor.fetchone()
        if employee_info:
            employee_id, department = employee_info
        else:
            employee_id, department = "Unknown", "Unknown"

        # Use a custom font and size
        font = ImageFont.truetype(font_path, font_size)

        # Draw bounding box around the face
        draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0), width=2)
        
        # Draw name and company
        draw.text((left + 6, bottom + 6), f"{name}", fill=(0, 0, 0), font=font)
        draw.text((left + 6, bottom + 20), f"Department: {department}", fill=(0, 0, 0), font=font)
        # Draw employee ID
        draw.text((left + 6, bottom + 32), f"Employee ID: {employee_id}", fill=(0, 0, 0), font=font)

        # Check if the worker is already checked in
        if check_in_time and not check_out_times[name_with_company]:
            # Compute check-out time
            check_out_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            check_out_times[name_with_company] = check_out_time
        else:
            # Compute check-in time
            check_in_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            check_in_times[name_with_company] = check_in_time

        # Get the current time
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save the image with appropriate filename and time-based information
        if check_in_times[name_with_company] and not check_out_times[name_with_company]:
            # Draw check-in time
            draw.text((left + 6, bottom + 44), f"Check-in: {check_in_time}", fill=(0, 0, 0), font=font)
            # Save image with check-in time
            image_path = f'{output_directory}/check_in_{current_time}_{employee_id}.png'
            pil_image.save(image_path)
            print(f"Saved check-in image: {image_path}")
        else:
            pass
            # # Draw check-out time
            # draw.text((left + 6, bottom + 44), f"Check-out: {check_out_time}", fill=(0, 0, 0), font=font)
            # # Save image with check-out time
            # image_path = f'{output_directory}/check_out_{current_time}_{employee_id}.png'
            # pil_image.save(image_path)
            # print(f"Saved check-out image: {image_path}")

        # Detect fatigue using eye aspect ratio (EAR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        for rect in rects:
            shape = predictor(gray, rect)
            shape_np = np.zeros((68, 2), dtype="int")
            for i in range(0, 68):
                shape_np[i] = (shape.part(i).x, shape.part(i).y)

            leftEye = shape_np[42:48]
            rightEye = shape_np[36:42]
            leftEAR = calculate_ear(leftEye)
            rightEAR = calculate_ear(rightEye)
            ear = (leftEAR + rightEAR) / 2.0

            if ear < EAR_THRESHOLD:
                blink_counter += 1
                if blink_counter >= CONSEC_FRAMES:
                    fatigue_detected = True
            else:
                blink_counter = 0
                fatigue_detected = False

            # Draw EAR and fatigue status
            draw.text((left + 6, bottom + 56), f"EAR: {ear:.2f}", fill=(0, 0, 0), font=font)
            draw.text((left + 6, bottom + 68), f"Fatigue: {'Yes' if fatigue_detected else 'No'}", fill=(0, 0, 0), font=font)

    # Display the frame or save it to a file
    cv2.imshow('Frame', cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Exit if 'q' key is pressed

# Release the video capture and close the database connection
cap.release()
cv2.destroyAllWindows()
conn.close()
