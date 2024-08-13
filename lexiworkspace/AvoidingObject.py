import cv2
import yolov5
from matplotlib import pyplot as plt
import mistyPy
from requests import request, Response
from datetime import datetime
from collections import namedtuple
import time
import json
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import torch
from mistyPy.Events import Events
from mistyPy.Robot import Robot
import threading

# Global flags
picture_taken = False
moving_around = False

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')

def save_image(image_data, file_name):
    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data)
    # Convert bytes to an image
    image = Image.open(BytesIO(image_bytes))
    # Save the image
    image.save(file_name)

def take_image():
    time.sleep(1)
    take_picture_response = misty.TakePicture(base64=True, fileName="misty_image.jpg", width=640, height=480, displayOnScreen=True, overwriteExisting=True)
    if take_picture_response.status_code == 200:
        print("Picture taken successfully!")
        image_data = take_picture_response.json().get('result', {}).get('base64', '')
        if image_data:
            # Save the image to a file
            save_image(image_data, "captured_image.jpg")
            img_path = 'captured_image.jpg'  # Replace with the path to your image
            img = cv2.imread(img_path)
            if img is not None:
                return model(img_path)
    return None

def detect_object(results):
    if results is not None:
        results.print()
        results.show()
        detections = results.pandas().xyxy[0]
        for index, row in detections.iterrows():
            label = row['name']
            confidence = row['confidence']
            print(f"Label: {label}, Confidence: {confidence}")
            if label == "cup" and confidence < 0.8:
                misty.Speak(f'Cup, confidence level is {confidence:.2f}')
                return True  # Object detected that requires moving around
    return False

def handle_time_of_flight(event_data):
    global picture_taken, moving_around
    distance = event_data['message']['distanceInMeters']
    sensor_id = event_data['message']['sensorId']
    
    # Set a threshold distance (in meters)
    threshold_distance = 0.3

    if sensor_id in ['toffc', 'toffr', 'toffl'] and distance < threshold_distance and not picture_taken and not moving_around:  # Check for Center Front sensor
        # Stop Misty
        misty.Stop()
        misty.MoveHead(30, 0, 0, 100)
        picture_taken = True
        print(f"Sensor: {sensor_id}, Distance: {distance} meters")

        # Take a picture with Misty
        results = take_image()
        if detect_object(results):
            move_around()

def move_misty():
    misty.MoveArms(50, 50)
    time.sleep(1)
    misty.DriveTime(25, 0, 2000)
    for i in range(2):
        misty.MoveArms(50, -50)
        time.sleep(1)
        misty.MoveArms(-50, 50)
        time.sleep(1)
        misty.MoveArms(50, 50)

def move_around():
    global picture_taken, moving_around
    if moving_around:
        return
    moving_around = True
    
    misty.DriveTime(linearVelocity=40, angularVelocity=-100, timeMs=4000, degree=90)
    time.sleep(3)
    misty.DriveTime(linearVelocity=50, angularVelocity=0, timeMs=1500)
    time.sleep(3)
    misty.DriveTime(linearVelocity=20, angularVelocity=100, timeMs=4000, degree=90)
    time.sleep(3)
    misty.DriveTime(linearVelocity=50, angularVelocity=0, timeMs=1000)
    time.sleep(1)
    misty.MoveHead(30, 0, 80, 100)
    time.sleep(1)
    results = take_image()
    detect_object(results)  # Only detect object but do not move again
    
    time.sleep(2)
    misty.DriveTime(linearVelocity=50, angularVelocity=0, timeMs=1000)
    time.sleep(3)
    misty.DriveTime(linearVelocity=15, angularVelocity=100, timeMs=3000, degree=90)
    time.sleep(3)
    misty.DriveTime(linearVelocity=50, angularVelocity=0, timeMs=1500)
    time.sleep(1)
    results = take_image()
    detect_object(results)

    # moving_around = False
    # picture_taken = False

    
    # misty.Speak(confidence)
    # if confidence < 0.6:
    #     misty.Speak("I don't know this object")
    # else:
    #     misty.Speak(f'I know this object its a {label}')



if __name__ == "__main__":
    misty = Robot('192.168.0.41')
    misty.ChangeLED(255, 255, 255)
    misty.DisplayImage("e_Admiration.jpg")
    # Misty's head goes to a default
    misty.MoveHead(0, 0, 0, 100)
    time.sleep(1)
    misty.RegisterEvent("TimeOfFlight", Events.TimeOfFlight, debounce=1000, keep_alive=True, callback_function=handle_time_of_flight)
    
    move_thread = threading.Thread(target=move_misty)
    move_thread.start()

    # Keep the script running
    while move_thread.is_alive():
        time.sleep(1)
