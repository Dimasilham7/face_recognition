from flask import Flask, jsonify, request, send_from_directory, render_template
import os
import cv2
import numpy as np
import face_recognition
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Initialize lists to store face encodings and names
list_of_face_encoding = []
known_face_names = []
employee_data = {}

# Function to retrieve employee department from the database based on name
def get_employee_department_from_database(name):
    conn = sqlite3.connect('company.db')
    c = conn.cursor()
    
    # Retrieve department from the employees table based on the name
    c.execute("SELECT department FROM employees WHERE name = ?", (name,))
    department = c.fetchone()
    
    # Close connection
    conn.close()
    
    # Return department or default to 'Unknown' if not found
    return department[0] if department else 'Unknown'

# Function to retrieve employee ID from the database based on name
def get_employee_id_from_database(name):
    conn = sqlite3.connect('company.db')
    c = conn.cursor()
    
    # Retrieve employee ID from the employees table based on the name
    c.execute("SELECT employee_id FROM employees WHERE name = ?", (name,))
    employee_id = c.fetchone()
    
    # Close connection
    conn.close()
    
    # Return employee ID or default to 'Unknown' if not found
    return employee_id[0] if employee_id else 'Unknown'

# Function to retrieve employee position from the database based on name
def get_employee_position_from_database(name):
    conn = sqlite3.connect('company.db')
    c = conn.cursor()
    
    # Retrieve position from the employees table based on the name
    c.execute("SELECT position FROM employees WHERE name = ?", (name,))
    position = c.fetchone()
    
    # Close connection
    conn.close()
    
    # Return position or default to 'Unknown' if not found
    return position[0] if position else 'Unknown'

# Function to record attendance in the database
def record_attendance(employee_id, check_in_time):
    conn = sqlite3.connect('company.db')
    c = conn.cursor()
    
    # Insert attendance record into the attendance table
    c.execute("INSERT INTO attendance (employee_id, check_in_time) VALUES (?, ?)", (employee_id, check_in_time))
    
    # Commit the transaction and close connection
    conn.commit()
    conn.close()

# Load the list of images
folder_path = 'ID/'
list_of_images = os.listdir(folder_path)
for image_name in list_of_images:
    image_path = os.path.join(folder_path, image_name)
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    list_of_face_encoding.append(encoding)
    name = os.path.splitext(image_name)[0]
    known_face_names.append(name)

    # Mock employee data, replace this with actual data from your database if available
    employee_data[name] = {
        'department': get_employee_department_from_database(name),
        'employee_id': get_employee_id_from_database(name),
        'check_in': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'position': get_employee_position_from_database(name)
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

# Function to determine if the person is fatigued (dummy implementation)
def is_fatigued():
    return True  # Replace with your actual logic

# Route to handle image upload and process face recognition
@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image = request.files['image']
    img = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
    frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect face locations and encodings
    face_locations = face_recognition.face_locations(frame_rgb)
    face_encodings = face_recognition.face_encodings(frame_rgb, face_locations)
    
    if not face_encodings:
        return jsonify({'name': 'No face detected'})

    # Match the detected face with known faces
    matches = face_recognition.compare_faces(list_of_face_encoding, face_encodings[0])
    
    if True in matches:
        first_match_index = matches.index(True)
        detected_name = known_face_names[first_match_index]
        employee_info = employee_data.get(detected_name, {})
        fatigue_status = "Fatigued" if is_fatigued() else "Not Fatigued"
        
        # Record attendance
        employee_id = employee_info.get('employee_id', 'Unknown')
        check_in_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        record_attendance(employee_id, check_in_time)

        return jsonify({
            'name': detected_name,
            'department': employee_info.get('department', 'Unknown'),
            'employee_id': employee_id,
            'check_in': check_in_time,
            'position': employee_info.get('position', 'Unknown'),
            'fatigue_status': fatigue_status
        })
    else:
        return jsonify({'name': 'Unknown'})

# Route to handle image registration
@app.route('/register', methods=['POST'])
def register():
    if 'image' not in request.files or 'name' not in request.form:
        return jsonify({'error': 'Image or name not provided'}), 400

    name = request.form['name']
    image = request.files['image']
    
    # Save the image in the 'ID' folder with the provided name
    image_path = os.path.join('ID', f"{name}.jpg")
    image.save(image_path)
    
    # Re-encode the new image and update the lists
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    list_of_face_encoding.append(encoding)
    known_face_names.append(name)

    # Update employee data
    employee_data[name] = {
        'department': get_employee_department_from_database(name),
        'employee_id': get_employee_id_from_database(name),
        'check_in': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'position': get_employee_position_from_database(name)
    }
    
    return jsonify({'message': 'Registration successful'})

if __name__ == '__main__':
    app.run(debug=True)
