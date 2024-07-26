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

# Global flag to ensure a picture is taken only once
picture_taken = False

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt')

def save_image(image_data, file_name):
    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data)
    # Convert bytes to an image
    image = Image.open(BytesIO(image_bytes))
    # Save the image
    image.save(file_name)

def handle_time_of_flight(event_data):
    global picture_taken
    distance = event_data['message']['distanceInMeters']
    sensor_id = event_data['message']['sensorId']
    
    # Set a threshold distance (in meters)
    threshold_distance = 0.5
    if sensor_id in ['toffc', 'toffr', 'toffl'] and distance < threshold_distance and not picture_taken:  # Check for Center Front sensor
        # Stop Misty
        misty.Stop()
        picture_taken = True
        print(f"Sensor: {sensor_id}, Distance: {distance} meters")

        # Take a picture with Misty
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
                    results = model(img_path)
                    results.print()
                    results.show()
                else:
                    print("Failed to load the saved image.")
            else:
                print("No image data returned.")
        else:
            print("Error taking picture:", take_picture_response.text)

def move_misty():
    misty.MoveArms(50, 50)
    time.sleep(1)
    misty.DriveTime(30, 0, 3000)
    for i in range(2):
        misty.MoveArms(50, -50)
        time.sleep(1)
        misty.MoveArms(-50, 50)
        time.sleep(1)
        misty.MoveArms(50, 50)

if __name__ == "__main__":
    misty = Robot('192.168.0.41')
    misty.ChangeLED(255, 255, 255)
    misty.DisplayImage("e_Admiration.jpg")
    # Misty's head goes to a default
    # misty.MoveHead(0, 0, 0, 100)
    time.sleep(1)

    misty.RegisterEvent("TimeOfFlight", Events.TimeOfFlight, debounce=1000, keep_alive=True, callback_function=handle_time_of_flight)
    
    move_thread = threading.Thread(target=move_misty)
    move_thread.start()

    # Keep the script running
    while move_thread.is_alive():
        time.sleep(1)
