# Table of Contents

- [Hand Chess Project](#hand-chess-project)
    - [Description](#description)
	- [Features](#features)
    - [Technologies Used](#technologies-used)
    - [How to Run the Project](#how-to-run-the-project)
        - [Note](#note)
    - [Instructions for Use](#instructions-for-use)
    - [Version 1](#version-1)
		- [Demo](#version-1-demo)
		- [Notes](#version-1-notes)
	- [Version 2](#version-2)
		- [Demo](#version-2-demo)
		- [Notes](#version-2-notes)
    - [License](#license)

# Hand Chess Project

## Description
Hand Chess is an innovative chess application that allows users to play  using hand gestures. With a webcam and hand-tracking technology, players can select and move pieces on a virtual chessboard simply using their index finger.


## Features
- Interactive chess game with gesture-based controls. 
- Real-time recognition of the index finger position.
- Simple and intuitive user interface.
- Support for legal moves according to chess rules.
- Visual feedback with highlighted squares and executed moves.


## Technologies Used
- **Python**: Main programming language.
- **Pygame**: For handling graphics and user interface.
- **OpenCV**: For image processing and gesture recognition.
- **Mediapipe**: For hand tracking and finger position detection.

## How to Run the Project

0. Ensure Python is installed:
	-  **If using Arch Linux** :
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
  	python src/main.py
	```

### Note

- If using Python 3, you may need to use `python3` instead of `python`, depending on your setup.
- You can install packages within the virtual environment using `pip`, and these installations won’t affect global Python installations.

## Instructions for use
- In the initial popup choose the webcam you would like to use.
- Position your index finger in front of the webcam to select pieces, index position is translated on the board and the user can maneuver the cursor through it.
- Pinch with any pair of fingers to make the click gesture (recommended to use thumb and middle finger, while pointing with the index).
- To quit the game press "esc" on the board.
- To save a game press "s" on the board.
- To load saved game press "l" on the board.

## Version 1 (Old)
<a id="version-1-demo"></a>
### Demo 
![Demo](img/Demo-v1.gif)
<a id="version-1-notes"></a>
### Notes
The project is in its early stages: cursor precision is highly unstable, and control gestures are not yet fully defined, resulting in difficult maneuverability for pieces and making some moves impossible.

## Version 2
<a id="version-2-demo"></a>
### Demo
![Demo](img/Demo-v2.gif)

<a id="version-2-notes"></a>
### Notes
- Pinch gesture developed, now all feasible moves are actually possible.
- Webcam source printed on screen with a grid board drawn on it, to be more usable for the user.
- Moves list added to the board frame.
- Game can be saved by pressing "s".
- Saved game can be loaded by pressing "l".

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
