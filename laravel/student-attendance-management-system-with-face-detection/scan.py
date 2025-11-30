import cv2
import cv2.face
import os
import numpy as np
from datetime import datetime
import sqlite3
import time
import sys

DATABASE = 'lms.db'

# Path to the directory containing images
img_dir='images'
images_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),img_dir)
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn
db = get_db_connection()
employees = db.execute('SELECT * FROM employees').fetchall()
db.close()

def isDataPresent(key,rowset):
    status=False
    for row in rowset:
        if row[0]==key:
            status=True
    return status
           
    

if not employees:
    print('Employee data not present to proceed')
    exit()
# Load pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize face recognition model (you need to train this with your dataset)
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("recognizer_model.yml")

id_to_name = {}
for employee in employees:
    id_to_name[employee[0]] = employee[2] + ' ' + employee[3]

def validate_identity(id,strName):
    if isDataPresent(id,employees):
        print('Validation successful for '+ strName +'!')
    else:
        print('Alert: Unauthorized access')

# Capture video from the camera
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the camera
    ret, frame = cap.read()
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    # Process each detected face
    for (x, y, w, h) in faces:
        # Extract the region of interest (ROI) which is the face
        face_roi = gray[y:y+h, x:x+w]
        
        # Perform face recognition
        label, confidence = recognizer.predict(face_roi)
        
        # If confidence is less than 100, recognize the face
        if confidence > 90:
            # Get the name corresponding to the recognized face ID
            name = id_to_name.get(label, "Unknown")
            
            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Display the name of the recognized person
            cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Mark attendance (skip if already marked for today)
                 
            validate_identity(label,name)
    
    # Display the frame
    cv2.imshow('Security check', frame)
    
    # Exit the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close the OpenCV windows
cap.release()
cv2.destroyAllWindows()
