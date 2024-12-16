# 🎄 MQTTPyGame: A Very Schier Xmas 🎅

Hey there! Welcome to **MQTTPyGame**, a fun little project I whipped up to bring some holiday cheer. It's a game where you help Santa blast messages coming from an MQTT broker.

## Features

- **Messages from the broker** show up in the game as "enemies" (naughty kids, maybe? 🤔).
- **Santa shoots candy canes** to eliminate those bad boys.
- **Mariah Carey** (of course) and some festive sound effects to complete the experience.

## What You Need

- **Python 3.9+** (or newer)
- A **Windows machine** (haven't tested on anything else XD)
- The files in this folder: all the images, sounds, and code

## How to Get Started

### 1. Install Python

If you don't have Python yet, grab it here. During the installation, make sure to check the box **Add Python to PATH** (super important).

### 2. Get the Project

Clone this repo (or download it as a ZIP) and open the folder:

```bash
git clone https://github.com/yourusername/mqttpygame.git
cd mqttpygame
```
## 3. Virtual Environment (Optional, but saves you from Python headaches)
Set up a virtual environment like this:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Run the Game
It's go time! Fire it up:

```bash
python MqttPyGame.py
```

## Share the Game
Wanna share the game without making people install Python? Here's how:

Install PyInstaller:
```bash
pip install pyinstaller
```
Build it into an executable:
```bash
pyinstaller --onefile --add-data "santa.png;." --add-data "cane.png;." --add-data "bg.jpg;." --add-data "mariah.mp3;." --add-data "explosion.mp3;." --add-data "game_over_santa.gif;." --add-data "seguiemj.ttf;." MqttPyGame.py
```
The .exe will show up in the dist folder. Zip it up with all the asset files, and boom—you've got a sharable Christmas gift. 🎁
