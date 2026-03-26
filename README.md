# IoT Assignment 1: MQTT Sensor Publisher/Subscriber

This project implements an IoT system using MicroPython on an ESP32 (or similar microcontroller) that connects to a Wi-Fi network, subscribes to an MQTT topic, publishes temperature and humidity data from a DHT11 sensor, and logs received messages to a CSV file.

## Features

- **Error Logging**: Creates and maintains an `error.log` file for debugging.
- **Configuration Management**: Reads Wi-Fi and MQTT settings from `config.txt`.
- **Wi-Fi Connectivity**: Connects to a specified access point.
- **MQTT Subscriber**: Listens for messages on a topic and logs data to `subscriber.csv`, with LED blinking on receipt.
- **MQTT Publisher**: Publishes sensor data every 15 seconds.
- **Sensor Integration**: Reads temperature and humidity from DHT11 sensor.
- **Timed Operation**: Runs for 5 minutes before disconnecting.

## Requirements

- MicroPython-compatible microcontroller (e.g., ESP32)
- DHT11 temperature and humidity sensor connected to Pin 22
- Wi-Fi access point
- MQTT broker
- Required MicroPython libraries: `network`, `machine`, `umqtt.robust`, `binascii`, `dht`

## Setup

1. **Hardware Setup**:
   - Connect DHT11 sensor to Pin 22 on the microcontroller.
   - Ensure the board has an LED (default "LED" pin).

2. **Configuration**:
   - Create a `config.txt` file with the following format:
     ```
     ACCESS_POINT_NAME=YourWiFiSSID
     ACCESS_POINT_PASSWORD=YourWiFiPassword
     MQTT_BROKER_HOSTNAME=your.mqtt.broker.com
     MQTT_BROKER_PORT=1883
     ```
   - Replace placeholders with actual values.

3. **Upload Code**:
   - Upload `launcher.py` to the microcontroller using tools like Thonny or ampy.

## Usage

1. Run `launcher.py` on the microcontroller.
2. The script will:
   - Create `error.log` and `subscriber.csv` if they don't exist.
   - Connect to Wi-Fi.
   - Start MQTT subscriber and publisher.
   - Publish sensor data every 15 seconds.
   - Log received messages to CSV and blink LED.
   - Run for 5 minutes, then disconnect.

3. Monitor output via serial console for status messages.

## Files

- `launcher.py`: Main script.
- `subscriber.csv`: Logs received MQTT messages (timestamp, temperature, humidity).

## Notes

- Student ID is hardcoded as "201938536" for digit sum calculation.
- Topic format: `/sensor/{mac_address}/{unix_timestamp}/`
- Client IDs include board ID and timestamp for uniqueness.
- Program handles keyboard interrupts gracefully.

## Troubleshooting

- Check `error.log` for any issues.
- Ensure `config.txt` has all required fields.
- Verify Wi-Fi and MQTT broker connectivity.
- Confirm DHT11 sensor is properly connected.</content>
<parameter name="filePath">c:\Users\nidhi\OneDrive\Desktop\IOT\Assign1\README.md