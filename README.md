<p align="center">
  <img src="Gcoder_banner.png" width="700">
</p>

# GCoder – PySide6 G-code Sender

A lightweight **Python GUI application for sending G-code commands** to CNC machines, 3D printers, or GRBL-based controllers over a serial connection.

Built using **PySide6 (Qt for Python)** and **PySerial**, GCoder provides a simple interface to:

- Send individual G-code commands
- Load and stream entire G-code files
- View controller responses in real-time
- Save session logs
- Navigate command history with arrow keys
- Automatically remember the last used COM port

---

# Features

## Serial Communication

- Connects to devices using **serial COM ports**
- Default baud rate: **115200**
- Automatic device response reading

## G-code Command Sender

- Send single commands manually
- Supports commands starting with:
  - `G`
  - `M`

**Example:**

```gcode
G0 X10 Y10
G1 X50 Y50 F300
M114
```
### File Streaming

- Load and send an entire G-code file
- Supported file types:
  - `.gcode`
  - `.nc`
  - `.txt`
- Ignores empty lines and comments starting with `;`
- Waits for `ok` response before sending the next line

## Real-time Log Window

- Shows sending and device responses in real-time
- Automatically scrolls to the newest message

**Example:**

```text
Sending: G0 X10
ok
Sending: G1 X50
ok
