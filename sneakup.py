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

def check_consecutive_distances(distances, count, threshold):
    consecutive_count = 0
    for i in range(len(distances) - 1):
        if abs(distances[i] - distances[i + 1]) <= threshold:
            consecutive_count += 1
            if consecutive_count >= count - 1:
                return True
        else:
            consecutive_count = 0
    return False

if __name__ == "__main__":
    misty = Robot('192.168.0.47')
 
    # Register the TimeOfFlight event
    misty.register_event("TimeOfFlight", Events.TimeOfFlight, debounce=80, keep_alive=True, callback_function=handle_time_of_flight)
    
    #reset
    misty.change_led(255, 255, 255)
    misty.display_image("e_Admiration.jpg")
    misty.move_head(0, 0, 0, 100)
    misty.move_arms(50,50)
    
    try:
        # Initialize distance collection
        distlist.clear()
        timestamped_distances.clear()
        
        similarity_threshold = 0.37  # Define your threshold for similarity
        consecutive_count = 10  # Define the number of consecutive distances required
        
        # Start driving forward
        #driveForward(duration_ms=10000)  # Drive for an initial 10 seconds
        misty.drive(100, 0)

        while True:
            # Collect distances every second
            start_time = time.time()
            end_time = start_time + 1  # Collect data for 1 second

            while time.time() < end_time:
                current_time = int(time.time())
                if current_time in timestamped_distances:
                    # Append the distance to the list if it was recorded at this second
                    distlist.append(timestamped_distances[current_time])
                    print(f"At {current_time} seconds: {timestamped_distances[current_time]} meters")
                    # Remove the timestamp to avoid re-appending
                    del timestamped_distances[current_time]
                    
                    # Ensure the list only contains the last 10 seconds of data
                    if len(distlist) > 10:
                        distlist.pop(0)
            
            # Check for consecutive distances within the threshold
            # Check for consecutive distances within the threshold
            if check_consecutive_distances(distlist, consecutive_count, similarity_threshold):
                
                # Stop Misty's movement immediately
                misty.stop()  # Ensure Misty stops before executing the next actions
                
                # Display the image and execute other actions
                misty.display_image("e_Contempt.jpg")
                misty.speak(text="What the?", pitch=2)
                misty.speak(text="is someone behind me?", pitch=1)
                misty.change_led(255, 165, 0)
                time.sleep(1)
                
                # Head turns slowly to 90 degrees
                for yaw_angle in [20, 30, 60, 90]:
                    misty.move_head(pitch=0, roll=0, yaw=yaw_angle)
                    time.sleep(1)

                # Body turns slowly around in place(hardwood)
                # misty.drive_track(leftTrackSpeed=200, rightTrackSpeed=-200)  # Adjust speeds for full circle
                # time.sleep(1.7)
                # Turn in a circle to face the other direction
                misty.drive_time(linearVelocity=0, angularVelocity=500, timeMs=9000)  # Adjust timeMs for the desired rotation duration
                time.sleep(1)
                misty.drive_time(linearVelocity=0, angularVelocity=100, timeMs=2000)  # Optional: Fine-tune the turn
                time.sleep(1)
                misty.drive_time(linearVelocity=0, angularVelocity=510, timeMs=4000)  # Adjust timeMs for the desired rotation duration
                time.sleep(1)
                # misty.drive_time(linearVelocity=0, angularVelocity=100, timeMs=2000)  # Optional: Fine-tune the turn
                # time.sleep(1)
                # misty.drive_time(linearVelocity=0, angularVelocity=480, timeMs=9000)  # Adjust timeMs for the desired rotation duration
                # time.sleep(1)
                
                # Head turns forward to face body
                for yaw_angle in [20, 30]:
                    misty.move_head(pitch=0, roll=0, yaw=yaw_angle)
                    time.sleep(1)
                
                
                # Look up and yell and throw arms up
                time.sleep(1)
                misty.display_image("e_Terror.jpg")
                for pitch_angle in [8, -13, -25, -40]:
                    misty.move_head(pitch=pitch_angle, roll=0, yaw=0)
                    time.sleep(1)
                misty.move_arms(-50, -50)
                misty.change_led(255, 0, 0)
                misty.speak(text="E EE EEEK!!!", pitch=8)
                
                # Run back
                misty.drive(linearVelocity=-70, angularVelocity=0)
                time.sleep(1)
                misty.stop()
                break  # Exit the loop to stop continuous driving

            else:
                #misty.speak("No one is following")
                # Continue driving forward if the condition is not met
                driveForward(duration_ms=10000)  # Continue driving forward

    finally:
        # Perform any cleanup
        misty.change_led(255, 255, 255)
        misty.display_image("e_Admiration.jpg")
        misty.move_head(0, 0, 0, 100)
        misty.move_arms(50,50)



