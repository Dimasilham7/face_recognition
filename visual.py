import os
import face_recognition
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Paths
known_faces_dir = 'ID/'
test_faces_dir = 'test_faces/'

# Initialize lists
known_face_encodings = []
known_face_names = []

# Load known faces
for image_name in os.listdir(known_faces_dir):
    image_path = os.path.join(known_faces_dir, image_name)
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
    name = os.path.splitext(image_name)[0]
    known_face_names.append(name)

# Initialize lists for true and predicted labels
true_labels = []
predicted_labels = []

# Load test faces and perform recognition
for label in os.listdir(test_faces_dir):
    label_dir = os.path.join(test_faces_dir, label)
    for image_name in os.listdir(label_dir):
        image_path = os.path.join(label_dir, image_name)
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            true_labels.append(label)
            predicted_labels.append(name)

# Calculate accuracy
accuracy = accuracy_score(true_labels, predicted_labels)
print(f'Accuracy: {accuracy * 100:.2f}%')

# Plot confusion matrix
cm = confusion_matrix(true_labels, predicted_labels, labels=known_face_names + ["Unknown"])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=known_face_names + ["Unknown"])

fig, ax = plt.subplots(figsize=(20, 20))
disp.plot(ax=ax)
plt.xticks(rotation=90)
plt.show()
