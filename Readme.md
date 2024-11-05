# Table of contents

- [[#Hand Chess Project|Hand Chess Project]]
	- [[#Hand Chess Project#Description|Description]]
	- [[#Hand Chess Project#Technologies Used|Technologies Used]]
	- [[#Hand Chess Project#How to Run the Project|How to Run the Project]]
		- [[#How to Run the Project#Note|Note]]
	- [[#Hand Chess Project#Instructions for Use|Instructions for Use]]
	- [[#Hand Chess Project#Version 1.0|Version 1.0]]
		- [[#Version 1.0#Demo|Demo]]
		- [[#Version 1.0#Notes|Notes]]
	- [[#Hand Chess Project#License|License]]

# Hand Chess Project

## Description
Hand Chess is an innovative chess application that allows users to play by using hand gestures. With a webcam and hand-tracking technology, players can select and move pieces on a virtual chessboard simply by using their index finger.

<!-- 
## Features
- Interactive chess game with gesture-based controls.
- Real-time recognition of the index finger position.
- Simple and intuitive user interface.
- Support for legal moves according to chess rules.
- Visual feedback with highlighted squares and executed moves.
-->

## Technologies Used
- **Python**: Main programming language.
- **Pygame**: For handling graphics and user interface.
- **OpenCV**: For image processing and gesture recognition.
- **Mediapipe**: For hand tracking and finger position detection.

## How to Run the Project

0. Ensure Python is installed:
	-  **For Arch Linux**:
	   1. Update package index:
		```bash
		sudo pacman -Syu
		```
	   2. Install Python:
		```bash
		sudo pacman -S python
		```
	   3. Install pip:
		```bash
		sudo pacman -S python-pip
		```

1. Clone the repository:
```bash
  git clone https://github.com/luigidannibale/hand-chess.git
  cd hand-chess
```

2. Create a virtual environment (optional but recommended):
``` bash
  python -m venv handchess-venv
  source handchess-venv/bin/activate
   ```
3. Install dependencies:
``` bash
  pip install -r requirements.txt
``` 
4. Run the main file:
```bash
  python main.py
```

### Note
- If using Python 3, you may need to use `python3` instead of `python`, depending on your setup.
- You can install packages within the virtual environment using `pip`, and these installations won’t affect global Python installations.

## Instructions for Use
- Position your index finger in front of the webcam to select pieces.
- Move your finger to move the cursor over the board and choose moves.
- Click on the board to make moves.

## Version 1.0
### Demo
![Demo](src/Demo-v1.gif)
### Notes
The project is in its early stages: cursor precision is highly unstable, and control gestures are not yet fully defined, resulting in difficult maneuverability for pieces and making some moves impossible.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
