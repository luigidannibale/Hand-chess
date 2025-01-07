
import os
import pygame
import chess
from board import draw_board, draw_pieces, draw_board_with_highlight
from board import BoardSquare
import mediapipe as mp
import cv2
import math



def handle_selection(board_square):
    """Gestisce la selezione di un pezzo."""
    print("Hai selezionato:", chess.square_name(board_square.square))
    return board_square

def handle_move(chess_board, move, board_square):
    """Gestisce la mossa di un pezzo."""
    chess_board.push(move)
    print(f"Mossa eseguita: {move.uci()}")
    return board_square

# Inizializza Pygame e crea la finestra
def initialize_game():

    # Configurazione generale
    SETTINGS = {
        "width": 640,
        "height": 640,
        "fps": 60,
        "colors": {
            "selection": (0, 204, 0),
            "move": (200, 200, 60),
            "pointer": (255, 0, 0)  # Rosso per il puntatore dell'indice
        }
    }

    pygame.init()
    win = pygame.display.set_mode((SETTINGS["width"], SETTINGS["height"]))
    pygame.display.set_caption("Chess Game")
    return win


def get_hand_landmarks():
    """Rileva la posizione della mano tramite la webcam e Mediapipe."""
    success, frame = cap.read()
    if not success:
        return None, None  # Ritorna None se la webcam non fornisce un frame valido
    
    # Rileva la mano
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        # Prendi il primo rilevamento e il punto del dito indice
        hand_landmarks = results.multi_hand_landmarks[0]
        
        return hand_landmarks
    
    return None

def get_index_finger_position():
    """Rileva la posizione del dito indice tramite la webcam e Mediapipe."""
    
    hand_landmarks = get_hand_landmarks()
    
    if hand_landmarks is not None:
        # Prendi il primo rilevamento e il punto del dito indice        
        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # Converti le coordinate in base alla risoluzione dello schermo e specchia sull'asse orizzontale
        x = int(index_finger_tip.x * SETTINGS["width"])
        y = int(index_finger_tip.y * SETTINGS["height"])
        flipped_x = SETTINGS["width"] - x  # Specchia l'asse orizzontale
        return flipped_x, y

    return None, None

def _close():
    pygame.quit()
    cap.release()
    hands.close()

def _main():

    # Configurazione generale
    SETTINGS = {
        "width": 640,
        "height": 640,
        "fps": 60,
        "colors": {
            "selection": (0, 204, 0),
            "move": (200, 200, 60),
            "pointer": (255, 0, 0)  # Rosso per il puntatore dell'indice
        }
    }

    # Mediapipe e OpenCV
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    cap = cv2.VideoCapture(0)  # Usa la webcam

    #TODO
    def is_pinch_gesture():
        """Funzione che deve capire se la mano sta eseguendo la gesture di pinch"""        
        # """
        # Classifica la posa della mano in base ai landmark rilevati da MediaPipe.

        # Parametri:
        # - hand_landmarks: Lista di landmark della mano rilevati da MediaPipe.

        # Restituisce:
        # - Una stringa che descrive la posa della mano.
        # """

        hand_landmarks_raw = get_hand_landmarks()            

        hand_landmarks_list = list(hand_landmarks_raw.landmark)

         # Landmark di riferimento per ogni dito
        wrist = hand_landmarks_list[0]               # Polso
        thumb_mcp = hand_landmarks_list[2]            # MCP pollice
        thumb_tip = hand_landmarks_list[4]            # Punta pollice
        index_finger_mcp = hand_landmarks_list[5]    # MCP indice
        index_finger_tip = hand_landmarks_list[8]    # Punta indice
        middle_finger_mcp = hand_landmarks_list[9]   # MCP medio
        middle_finger_tip = hand_landmarks_list[12]  # Punta medio
        ring_finger_mcp = hand_landmarks_list[13]    # MCP anulare
        ring_finger_tip = hand_landmarks_list[16]    # Punta anulare
        pinky_finger_mcp = hand_landmarks_list[17]   # MCP mignolo
        pinky_finger_tip = hand_landmarks_list[20]   # Punta mignolo

        # Funzione per calcolare la distanza 3D
        def distance_3d(point1, point2):
            return math.sqrt((point1.x - point2.x) ** 2 +
                            (point1.y - point2.y) ** 2 +
                            (point1.z - point2.z) ** 2)

        # Funzione per determinare se un dito è "aperto" basato sulla distanza
        def is_finger_open(mcp, tip, threshold=0.15):
            return distance_3d(mcp, tip) > threshold

        # Controlla lo stato del dito indice
        index_open = is_finger_open(index_finger_mcp, index_finger_tip)

        # Controlla lo stato delle altre dita
        thumb_open = is_finger_open(thumb_mcp, thumb_tip)    
        middle_open = is_finger_open(middle_finger_mcp, middle_finger_tip)
        ring_open = is_finger_open(ring_finger_mcp, ring_finger_tip)
        pinky_open = is_finger_open(pinky_finger_mcp, pinky_finger_tip)

        print("Frame ----------")
        print("Pollice - Distanza MCP-Tip =", distance_3d(thumb_mcp, thumb_tip))
        print("Indice - Distanza MCP-Tip =", distance_3d(index_finger_mcp, index_finger_tip))
        print("Medio - Distanza MCP-Tip =", distance_3d(middle_finger_mcp, middle_finger_tip))
        print("Anulare - Distanza MCP-Tip =", distance_3d(ring_finger_mcp, ring_finger_tip))
        print("Mignolo - Distanza MCP-Tip =", distance_3d(pinky_finger_mcp, pinky_finger_tip))
        # if thumb_open:
        #     print("Pollice puntato")
        # if index_open:
        #     print("Indice puntato")
        # if middle_open:
        #     print("Medio puntato")
        # if ring_open:
        #     print("Anulare puntato")
        # if pinky_open:
        #     print("Mignolo puntato")        
        print("-------------------")
        return True
            
    def click_point(board_square):
        nonlocal selected_square, moved_square, selected, moved
        # Gestisci la selezione o il movimento sulla scacchiera
        if selected_square is not None:            
            move = chess.Move(selected_square.square, board_square.square)            
            if move in chess_board.legal_moves:
                moved_square = handle_move(chess_board, move, board_square)
                moved = True
                selected_square = None
                selected = False
            elif chess_board.piece_at(board_square.square):
                selected_square = handle_selection(board_square)
                selected = True
        elif chess_board.piece_at(board_square.square):
            selected_square = handle_selection(board_square)
            selected = True

    def manage_index(x, y):
        #TODO
        def is_position_valid(x,y):
            """Funzione che deve capire se la posizione dell'indice è valida, quindi sulla scacchiera"""
            return True

        nonlocal selected_square, moved_square, selected, moved    

        # Se la posizione non è valida esci
        if not is_position_valid(x,y):
            return

        # Ottieni il BoardSquare dal tocco o dal puntatore
        board_square = BoardSquare.from_coordinates(x, y)

        # Disegna un puntatore rosso dove si trova l'indice
        pygame.draw.circle(win, SETTINGS["colors"]["pointer"], (x, y), radius=10)
        
        if is_pinch_gesture():
            click_point(board_square)
        
    win = initialize_game()
    chess_board = chess.Board()
    clock = pygame.time.Clock()
    selected_square, moved_square = None, None
    selected, moved = False, False
    # Pulisci la finestra
    
    win.fill((255, 255, 255))  # Riempie la finestra con un colore di sfondo bianco
    
    while True:
        clock.tick(SETTINGS["fps"])

        

        # Usa Mediapipe per ottenere la posizione dell'indice
        x, y = get_index_finger_position()

        # Aggiornamento della scacchiera
        if selected and selected_square:
            draw_board_with_highlight(win, selected_square.col, selected_square.row, SETTINGS["colors"]["selection"])
        elif moved and moved_square:
            draw_board_with_highlight(win, moved_square.col, moved_square.row, SETTINGS["colors"]["move"])
        else:
            draw_board(win)        
        draw_pieces(win, chess_board)
            
        
        if x is not None and y is not None:
            manage_index(x, y)


        # Gestione eventi di uscita
        for event in pygame.event.get():            
            if event.type == pygame.QUIT:
                _close()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                manage_index(mouse_x, mouse_y)                

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    _close()
                    return
                elif event.key == pygame.K_t:  # Controllo per il tasto T
                    print("The 'T' key was pressed!")
                    # Inserisci qui la logica che vuoi eseguire quando si preme T

        pygame.display.update()

        # Verifica esito della partita
        if chess_board.outcome():
            print("La partita è finita:", chess_board.outcome())
            break


