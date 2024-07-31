import time
from mistyPy.Events import Events
from mistyPy.Robot import Robot

# Initialize list to store distances
distlist = []
timestamped_distances = {}  # Dictionary to store distances with timestamps

def handle_time_of_flight(event_data):
    distance = event_data['message']['distanceInMeters']
    sensor_id = event_data['message']['sensorId']
   
    if sensor_id == 'tofr':  # Check for the specific rear sensor
        current_time = int(time.time())  # Use timestamp for collection
        timestamped_distances[current_time] = distance

def driveForward(duration_ms):
    misty.drive_time(linearVelocity=40, angularVelocity=0, timeMs=duration_ms)

def all_distances_within_threshold(distances, threshold):
    if len(distances) < 2:
        return False  # Not enough data to determine similarity
    
    base_distance = distances[0]
    return all(abs(d - base_distance) <= threshold for d in distances)

#___________________________________________________________________________________________________________________
if __name__ == "__main__":
    misty = Robot('192.168.0.41')
 
    # Register the TimeOfFlight event
    misty.register_event("TimeOfFlight", Events.TimeOfFlight, debounce=80, keep_alive=True, callback_function=handle_time_of_flight)
 
    try:
        # Initialize distance collection
        distlist.clear()
        timestamped_distances.clear()
        
        similarity_threshold = 0.35  # Define your threshold for similarity
        
        # Start driving forward indefinitely
        while True:
            driveForward(duration_ms=15000)  # Drive for 15 seconds

            start_time = time.time()
            end_time = start_time + 15  # 15 seconds from start time

            while time.time() < end_time:
                current_time = int(time.time())
                if current_time in timestamped_distances:
                    # Append the distance to the list if it was recorded at this second
                    distlist.append(timestamped_distances[current_time])
                    print(f"At {current_time} seconds: {timestamped_distances[current_time]} meters")
                    # Remove the timestamp to avoid re-appending
                    del timestamped_distances[current_time]
                    
                    # Ensure the list only contains the last 15 seconds of data
                    if len(distlist) > 15:
                        distlist.pop(0)
                    
                

            # Determine if all distances are within the threshold
            if all_distances_within_threshold(distlist, similarity_threshold):
                time.sleep(1)  # Wait for 1 second
                misty.display_image("e_Contempt.jpg ")
                #misty.speak("Something might be following. Stopping.")
                misty.change_led(255,165,0)
                misty.speak(text= "what the?", pitch= 0)

                #misty.stop()  # Stop the robot
                #head turns slowly to 90degrees
                misty.move_head(pitch= 0, roll= 0, yaw=-20 )
                time.sleep(1)
                misty.move_head(pitch= 0, roll= 0, yaw=-30 )
                time.sleep(1)
                misty.move_head(pitch= 0, roll= 0, yaw=-60 )
                time.sleep(1)
                misty.move_head(pitch= 0, roll= 0, yaw=-90 )
                time.sleep(1)


                # #body turns slowly  around
                misty.drive_arc(30, 0, 4000)
                misty.drive_track(leftTrackSpeed= 600,rightTrackSpeed= 0)
                time.sleep(2)
                

                #head turns forward to face body
                misty.move_head(pitch= 0, roll= 0, yaw=20 )
                time.sleep(1)
                misty.move_head(pitch= 0, roll= 0, yaw=30 )
                time.sleep(1)
                misty.change_led(255,0,0)

                #look up and yell and throw arms up
                time.sleep(1)
                misty.display_image("e_Terror.jpg ")
                misty.move_head(pitch= 8, roll= 0, yaw=0 )
                time.sleep(1)
                misty.move_head(pitch= -13, roll= 0, yaw=0 )
                time.sleep(1)
                misty.move_head(pitch= -25, roll= 0, yaw=0 )
                time.sleep(1)
                misty.move_head(pitch= -40, roll= 0, yaw=0 )
                misty.move_arms(-50,-50)
                misty.speak(text= "E EE EEEK!!!", pitch= 8)


                # run back
                misty.drive_time(linearVelocity= -50, angularVelocity= 0, timeMs= 4000)
                misty.stop()
                break  # Exit the loop to stop continuous driving
            else:
                misty.speak("No one following. Continuing forward.")
                # If you want to continue moving forward, you need to start another drive session:
                # Loop will restart driving forward

    finally:
        # Perform any cleanup
        misty.change_led(255, 255, 255)
        misty.display_image("e_Admiration.jpg")
        misty.move_head(0, 0, 0, 100)
