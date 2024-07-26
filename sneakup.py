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
    misty.DriveTime(linearVelocity=40, angularVelocity=0, timeMs=duration_ms)
 
def are_distances_similar(distances, threshold):
    if len(distances) < 2:
        return False  # Not enough data to determine similarity
   
    for i in range(1, len(distances)):
        if abs(distances[i] - distances[i - 1]) > threshold:
            return False
    return True
 
if __name__ == "__main__":
    misty = Robot('192.168.0.41')
 
    # Register the TimeOfFlight event
    misty.RegisterEvent("TimeOfFlight", Events.TimeOfFlight, debounce=80, keep_alive=True, callback_function=handle_time_of_flight)
 
    try:
        # Initialize distance collection
        distlist.clear()
        timestamped_distances.clear()
 
        # Start driving forward
        driveForward(duration_ms=15000)  # Drive for 10 seconds
 
        start_time = time.time()
        end_time = start_time + 15  # 10 seconds from start time
 
        while time.time() < end_time:
            current_time = int(time.time())
            if current_time in timestamped_distances:
                # Append the distance to the list if it was recorded at this second
                distlist.append(timestamped_distances[current_time])
                print(f"At {current_time} seconds: {timestamped_distances[current_time]} meters")
                # Remove the timestamp to avoid re-appending
                del timestamped_distances[current_time]
           
            time.sleep(1)  # Wait for 1 second
 
        # Determine if distances are similar enough
        similarity_threshold = 0.40  # Define your threshold for similarity
        if are_distances_similar(distlist, similarity_threshold):
            print("Something might be following. Stopping.")
            misty.Stop()  # Stop the robot
        else:
            print("No clear sign of following. Continuing forward.")
            # If you want to continue moving forward, you need to start another drive session:
            driveForward(duration_ms=10000)  # Drive forward for another 10 seconds
 
    finally:
        # Perform any cleanup
        misty.ChangeLED(255, 255, 255)
        misty.DisplayImage("e_Admiration.jpg")
        misty.MoveHead(0, 0, 0, 100)