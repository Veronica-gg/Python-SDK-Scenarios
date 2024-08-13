import mistyPy
from mistyPy.Robot import Robot
import time
import cv2
import numpy as np
import os
import base64
from io import BytesIO
from PIL import Image
import torch 

# Define the path to the YOLOv5 model
current_directory = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_directory, "yolov5s.pt")  # Update with your model path

# Load YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)

def greeting(misty):
    misty.Speak("Hey how you doin today")  

def save_image(image_data, file_name):
    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data)
    # Convert bytes to an image
    image = Image.open(BytesIO(image_bytes))
    # Save the image
    image.save(file_name)

def capture_image(misty):
    #misty take picture with its camera
    take_picture_response = misty.TakePicture(base64=True, fileName="misty_image.jpg", width=640, height=480, displayOnScreen=True, overwriteExisting=True)
    if take_picture_response.status_code == 200:
        image_data = take_picture_response.json().get('result', {}).get('base64', '')
        if image_data:
            # Save the image to a file
            save_image(image_data, "captured_image.jpg")
            return "captured_image.jpg"
        else:
            print("No image data returned.")
    else:
        print("Error taking picture:", take_picture_response.text)
    return None

def show_image(file_name):
    #read the image taken
    img = cv2.imread(file_name)
    if img is not None:
        cv2.imshow("Captured Image", img)
        cv2.waitKey(2)  #wait 2sec 
        cv2.destroyAllWindows()
    else:
        print("Failed to load the image.")

def detect_person(img_path):
    #perform detection
    results = model(img_path)
    
    # display results
    results.print()
    results.show()

    # Get detections in pandas DataFrame format
    detections = results.pandas().xyxy[0]

    # check for the confidence level of the object being detected as a person
    for index, row in detections.iterrows():
        label = row['name']
        confidence = row['confidence']
        print(f"Label: {label}, Confidence: {confidence}")

        if label == "person" and confidence > 0.65:
            return True

    return False


if __name__ == "__main__":
    misty = Robot('192.168.0.41')

    misty.MoveHead(-15, 0, 0)
    misty.ChangeLED(125, 80, 30)
    
    misty.Drive(280,10)
    misty.MoveHead(8,0,0)
    time.sleep(1)
    misty.ChangeLED(255,0,255)
    misty.DisplayImage("e_ContentLeft.jpg")
    
    misty.MoveHead(0,0,-30)
    time.sleep(1)
    misty.DisplayImage("e_ContentRight.jpg")
    misty.MoveHead(0,0,40)
    time.sleep(0.5)
    misty.MoveHead(0,0,-30)
    time.sleep(0.5)
    time.sleep(0.5)
    misty.MoveArms("left", 50)
    misty.MoveArms("both",90)
    misty.Drive(60,0)
    misty.MoveHead(-10, 80 ,0 ,100)
    time.sleep(2)
    misty.MoveHead(0,0,70)
    time.sleep(1)
    misty.MoveHead(-30,10,10)
    time.sleep(0.5)
    misty.MoveArms(40, 40, 100, 100)

    #take picture from mistys camera
    image_file = capture_image(misty)
        
    if image_file:
        #display the image
        show_image(image_file)
            
        # Perform detection
        if detect_person(image_file):
            time.sleep(1)
            misty.Stop()
            greeting(misty)#greet the person if detects any
        else:
            print("No person detected.")
        
    
    