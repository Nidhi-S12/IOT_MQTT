## Task 1 : Create an empty error log file

import time  
import os    
import sys   
import network 
import machine 
from umqtt.robust import MQTTClient
import binascii
import dht
from machine import Pin

# Step 1.1: Check if 'error.log' exists and delete if present
try:
    # Attempt to open file if present in read mode; if successful, it means the file exists. If not, it raises OSError and we proceed for file creation
    with open('error.log', 'r') as f:
        pass  
    os.remove('error.log')  # Delete existing file 
except OSError:
    pass

# Step 1.2: Create new empty 'error.log' file. If not able to create, raise OSError
try:
    with open('error.log', 'w') as f:
        f.write('')  
except OSError as e:
    raise OSError(f"Failed to create 'error.log': {e}")

# Step 1.3: Define logging function
def log_error(message: str):
    """Append a timestamped error message to 'error.log'."""
    try:
        timestamp = str(int(time.time()))  # Unix timestamp
        log_line = f"{timestamp}: {message}\n" 
        with open("error.log", "a") as f:  # Append logs
            f.write(log_line)  
    except Exception as e:      # If even logging fails, show critical error and stop
        print(f"CRITICAL LOG FAIL: {e}. Message: {message}")
        sys.exit(1)  

# Testing : Append to verify log_error 
# log_error("Task 1 test")  
# print("Append done check file:")  
# with open('error.log', 'r') as f:
#     print(f.read())          
# print(os.listdir())

# ----------------------------------------------------------------------------- 

# Task 2 : Check and read config.txt for Access Point and MQTT broker connection details

def read_config():
    config_file = 'config.txt'
    config = {}
    
    # Check if file exists and is readable
    try:
        with open(config_file, 'r') as f:
            lines = f.readlines()
    except OSError as e:
        log_error(f"Cannot open/read {config_file}: {e}")
        raise SystemExit(f"Config file missing or unreadable: {e}")

    # Parse the config file 
    for line in lines:
        line = line.strip()
        if '=' in line and not line.startswith('#'):  # Skip empty comments
            key, value = line.split('=', 1)
            key = key.strip().upper()
            value = value.strip()
            config[key] = value  # Store as-is 
    
    # Check if required fields exist in the config file
    required = {'ACCESS_POINT_NAME', 'ACCESS_POINT_PASSWORD', 'MQTT_BROKER_HOSTNAME', 'MQTT_BROKER_PORT'}
    missing = required - set(config.keys())
    if missing:
        log_error(f"Missing config keys: {', '.join(missing)}")
        raise SystemExit(f"Invalid config: Missing {', '.join(missing)}")

    return config

# Testing : Read and verify config
try:
    config = read_config()
    print("Config file has all required keys.")
    print(config)
except SystemExit as e:
    print(f"Failed to read config details: {e}, terminating")

# ----------------------------------------------------------------------------- 

# Task 3 : Digit sum calculation

STUDENT_ID = "201938536"
try:  
    DIGIT_SUM = sum(int(digit) for digit in STUDENT_ID)        
    print(f"\nDIGIT_SUM = {DIGIT_SUM} (from {STUDENT_ID})")
except ValueError as e:
    log_error(f"Invalid character in STUDENT_ID: {e}")
    raise SystemExit("Invalid student ID , terminating.")

# ----------------------------------------------------------------------------- 

#Task 4 : Create a variable called “UNIX_TS”, which contains the Unix time stamp
try:
    UNIX_TS = int(time.time()) 
    print("\nUNIX timestamp successfully created.")
    print("UNIX_TS =", UNIX_TS)
except Exception as e:
    log_error(f"Failed to create UNIX_TS: {e}")
    raise SystemExit("Unable to obtain Unix timestamp, terminating.")

# ----------------------------------------------------------------------------- 

#Task 5: Establish a wireless connection with the AP

def connect_wifi(ssid, password, timeout=20):
    """ Establish a wireless connection """
    # Step 5.1: Initialise Wi-Fi interface as a station
    wlan = network.WLAN(network.STA_IF)

    # Step 5.2: Activate the interface
    wlan.active(True)
    print("\nWi-Fi interface activated.")

    # Step 5.3: Connect to the access point using config details
    print(f"Connecting to Wi-Fi network '{ssid}'") 
    wlan.connect(ssid, password)

    # Step 5.4: Wait until timeout for connection to be established
    start_time = time.time()           
    while not wlan.isconnected():        
        if time.time() - start_time > timeout:  
            error_msg = f"Wi-Fi connection timeout ({timeout}s) at UNIX_TS={UNIX_TS}"
            log_error(error_msg)         
            raise OSError("Failed to connect to Wi-Fi within timeout.")  
        time.sleep(1)

    # Step 5.5: Confirm success and return interface
    ip_addr = wlan.ifconfig()[0]
    print(f"Wi-Fi connected: IP={ip_addr} at UNIX_TS={UNIX_TS}")
    return wlan

# Connect using config details
ssid = config["ACCESS_POINT_NAME"]      
password = config["ACCESS_POINT_PASSWORD"]  

wlan = connect_wifi(ssid, password)

# ----------------------------------------------------------------------------- 

# Task 6 : Implement and launch the MQTT subscriber

# Step 6.1 : Setup Led 
led = machine.Pin("LED", machine.Pin.OUT)

# Step 6.2: Get MAC address of wifi interface and board ID 
try:
    mac_bytes = wlan.config('mac')
    mac = binascii.hexlify(mac_bytes).decode().lower()  # Lowercase hex, no colons

    board_id_bytes = machine.unique_id()
    board_id = binascii.hexlify(board_id_bytes).decode().upper() 

except Exception as e:
    log_error(f"Failed to read MAC or BOARD_ID: {e}")
    raise SystemExit("Unable to retrieve device info, terminating.")

# Step 6.3: Define MQTT parameters
topic = f"/sensor/{mac}/{UNIX_TS}/"
client_idSub = f"{board_id}-{UNIX_TS}-sub"
broker = config["MQTT_BROKER_HOSTNAME"]
port = int(config["MQTT_BROKER_PORT"])
print(f"\nMQTT Subscriber Topic: {topic}")
print(f"Client ID of Subscriber: {client_idSub}")

# Step 6.4: Create subscriber.csv 
try:
    if "subscriber.csv" not in os.listdir():
        with open("subscriber.csv", "w") as f:
            f.write("UNIX_TS, C, %\n")
        print("\nCreated new subscriber.csv file.")
    else:
        print("\nsubscriber.csv file already exists, appending new data.")
except Exception as e:
    log_error(f"Failed to create subscriber.csv: {e}")
    raise SystemExit("Unable to initialize subscriber file, terminating.")

# Step 6.5 : Define subscriber callback
def message_callback(topic, msg, *args):
    """Callback executed whenever a message is received."""
    try:
        payload = msg.decode('utf-8')  # Decode message and split into parts
        parts = [p.strip() for p in payload.split(",")]
        
        #Parse expected parts
        if len(parts) >= 6:     
            unix_ts = parts[0]  # Unix timestamp
            temp = parts[1]     # Temperature in Celsius
            hum = parts[3]      # Humidity in percentage

            # Write new line to CSV 
            with open("subscriber.csv", "a") as f:
                f.write(f"{unix_ts},{temp},{hum}\n")

            # Blink LED for 1 second
            led.on()
            time.sleep(1)
            led.off()

            print(f"Message received : TS:{unix_ts}, Temp:{temp}C, Hum:{hum}%")
        else:
            raise ValueError(f"Malformed MQTT message (expected 6 parts, got {len(parts)}): {payload}")
    except Exception as e:
        log_error(f"Error in message_callback: {e} | Payload: {payload}")

# Step 6.6: Establish MQTT connection
try:
    client = MQTTClient(client_idSub, broker, port)
    client.set_callback(message_callback)
    client.connect()
    client.subscribe(topic)
    print("\nMQTT Subscriber connected and subscribed to topic successfully!")
except Exception as e:
    log_error(f"MQTT Subscriber connection failed: {e}")
    raise RuntimeError("Failed to connect to MQTT broker, terminating.")

# Step 6.7: Verify subscriber connection 
try:
    print("Subscriber ready and listening in background.")
except Exception as e:
    log_error(f"Subscriber setup error: {e}")
    client.disconnect()
    raise SystemExit("Subscriber encountered an error, terminating.")


# ----------------------------------------------------------------------------- 

# Task 7 : Wait 15 seconds before launching the publisher
print("\nWaiting 15 seconds before starting publisher...")
time.sleep(15)

# ----------------------------------------------------------------------------- 

#Task 8 : Implement and launch the MQTT publisher & Task 9 : Disconnect after 5 minutes

#Step 8.1: Setup DHT11 sensor
dht_sensor = dht.DHT11(Pin(22))

#Step 8.2: MQTT Publisher parameters
client_idPub = f"{board_id}-{UNIX_TS}-pub"
print(f"\nMQTT Publisher Topic: {topic}")
print(f"Client ID of Publisher: {client_idPub}")

# Step 8.3: Establish MQTT Publisher connection
try:
    pub_client = MQTTClient(client_idPub, broker, port)  
    pub_client.connect()  
    print("\nMQTT Publisher connected to broker!")
except Exception as e: 
    log_error(f"Publisher connect failed: {e}")  
    raise RuntimeError("MQTT broker connection failed, terminating.") 

# Step 8.4: Start reading sensor 
def read_dht11(max_attempts=10):
    """Reading DHT data up to 10 times"""

    for attempt in range(max_attempts):
        try:
            dht_sensor.measure()  
            temp = dht_sensor.temperature()  
            hum = dht_sensor.humidity()      
            if temp is not None and hum is not None:  
                return temp, hum
        except Exception:
            time.sleep(2) 

    log_error("DHT11 sensor failed after 10 attempts.")  
    raise OSError("Sensor values unavailable after 10 reads, terminating.")  

#  -----------------------------------------------------------------------------

# Last part of Task 8 and Task 9 : Publisher loop with 5 minute disconnection

print("\nRunning system for 5 minutes before disconnection...")
start_time = time.time()
run_duration = 300 # 5 minutes = 300 seconds
try:
    while time.time() - start_time < run_duration:
        # Read and publish sensor data every 15 seconds
        temp, hum = read_dht11()
        current_ts = int(time.time())   # remove this if they want the initial timestamp and replace with UNIX_TS
        message = f"{current_ts}, {temp}, C, {hum}, %, {DIGIT_SUM}"
        pub_client.publish(topic, message)
        print(f"Published to {topic}: {message}")
        
        # Subscriber checks for incoming messages
        try:
            client.check_msg()    # Using non-blocking approach so the loop is not stalled 
        except Exception as e:
            log_error(f"Subscriber check_msg error: {e}")
        time.sleep(15)


    # After 5 minutes, disconnect both 
    print("\n 5 minutes have elapsed, disconnecting MQTT clients...")
    try:
        client.disconnect()
        print("Subscriber disconnected successfully.")
    except Exception as e:
        log_error(f"Error disconnecting subscriber: {e}")
    try:
        pub_client.disconnect()
        print("Publisher disconnected successfully.")
    except Exception as e:
        log_error(f"Error disconnecting publisher: {e}")

    print("Program completed successfully. All connections closed.")
    sys.exit()

except KeyboardInterrupt:
    print("Program interrupted by user.")
    try:
        client.disconnect()
        pub_client.disconnect()
    except:
        pass
    sys.exit()
except Exception as e:
    log_error(f"Error during execution: {e}")
    raise SystemExit("Program terminated due to error.")

