# NADAF-HOME (IoT Home Automation)

A complete IoT Home Automation project featuring an ESP8266 microcontroller and a Python Flask backend dashboard.

## 🌟 Features
- Beautiful, modern web dashboard to control your home devices.
- Two-way synchronization: physical button presses on the hardware update the web UI instantly.
- Local SQLite database (`devices.db`) to persist device states.
- Real-time hardware connectivity monitoring.

## 🛠️ Components Required
- 1x NodeMCU ESP8266 board
- 1x 4-Channel Relay Module (Active LOW)
- 4x Push Buttons (or standard wall switches)
- Breadboard & Jumper wires
- 5V Power Supply (for the Relay Module and ESP8266)

## 🔌 Circuit & Connections
The system controls 4 relays and reads from 4 physical buttons. The buttons are configured using the internal pull-up resistors (`INPUT_PULLUP`), which means they should be wired directly between the specified ESP8266 pin and Ground (`GND`).

### Relay Connections:
| Device Name | Relay Pin on ESP8266 |
|-------------|----------------------|
| Light 1     | **D3** (GPIO 0)      |
| Light 2     | **D4** (GPIO 2)      |
| Light 3     | **D5** (GPIO 14)     |
| Hall Fan    | **D6** (GPIO 12)     |

### Button Connections:
| Physical Button | Button Pin on ESP8266 |
|-----------------|-----------------------|
| Light 1 Button  | **D1** (GPIO 5)       |
| Light 2 Button  | **D2** (GPIO 4)       |
| Light 3 Button  | **D7** (GPIO 13)      |
| Hall Fan Button | **D8** (GPIO 15)      |

*(Note: Connect one side of the button to the specified pin, and the other side to `GND`)*

## 🚀 How to Run the Project

### 1. Hardware Setup (ESP8266)
1. Wire all the components as specified in the connections table above.
2. Open the `NADAF_HOME/NADAF_HOME.ino` file using the Arduino IDE.
3. Update the Wi-Fi credentials to match your home network:
   ```cpp
   const char *ssid = "YOUR_WIFI_SSID";
   const char *password = "YOUR_WIFI_PASSWORD";
   ```
4. Update the IP address in `serverGetUrl` and `serverPostUrl` to match your PC's local IP address.
5. Connect your ESP8266 to your PC via USB and click **Upload**.

### 2. Backend Setup (Python Flask)
1. Ensure you have Python installed on your PC.
2. Open a terminal or command prompt inside the `Server/` directory.
3. Install the required `flask` library:
   ```bash
   pip install flask
   ```
4. Start the backend server by running:
   ```bash
   python Main.py
   ```
5. The server will boot up and automatically initialize the database. Open your web browser and navigate to `http://localhost:5000` or `http://<YOUR_PC_IP>:5000` to control your home!

---

👨‍💻 **Developed by:** SAMEER NADAF  
🔗 **GitHub Repository:** [https://github.com/Sameergudusabnadaf/NADAF-HOME](https://github.com/Sameergudusabnadaf/NADAF-HOME)