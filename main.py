
import os
import pygame
import chess
from board import draw_board, draw_pieces, draw_board_with_highlight
import mediapipe as mp
import cv2

# Configura la variabile d'ambiente per SDL
os.environ["SDL_VIDEODRIVER"] = "wayland"

# Configurazione generale
SETTINGS = {
    "width": 640,
    "height": 640,
    "fps": 30,
    "colors": {
        "selection": (200, 150, 90),
        "move": (200, 200, 60),
        "pointer": (255, 0, 0)  # Rosso per il puntatore dell'indice
    }
}

# Funzioni per gestione della selezione e movimento
def handle_selection(square, col, row):
    """Gestisce la selezione di un pezzo."""
    print("Hai selezionato:", chess.square_name(square))
    return square, col, row

def handle_move(chess_board, move, col, row):
    """Gestisce la mossa di un pezzo."""
    chess_board.push(move)
    print(f"Mossa eseguita: {move.uci()}")
    return col, row

# Inizializza Pygame e crea la finestra
def initialize_game():
    pygame.init()
    win = pygame.display.set_mode((SETTINGS["width"], SETTINGS["height"]))
    pygame.display.set_caption("Chess Game")
    return win

# Mediapipe e OpenCV
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
cap = cv2.VideoCapture(0)  # Usa la webcam

def get_index_finger_position():
    """Rileva la posizione del dito indice tramite la webcam e Mediapipe."""
    success, frame = cap.read()
    if not success:
        return None, None  # Ritorna None se la webcam non fornisce un frame valido
    
    # Rileva la mano
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        # Prendi il primo rilevamento e il punto del dito indice
        hand_landmarks = results.multi_hand_landmarks[0]
        index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        # Converti le coordinate in base alla risoluzione dello schermo e specchia sull'asse orizzontale
        x = int(index_finger_tip.x * SETTINGS["width"])
        y = int(index_finger_tip.y * SETTINGS["height"])
        flipped_x = SETTINGS["width"] - x  # Specchia l'asse orizzontale
        return flipped_x, y

    return None, None


def main():
    win = initialize_game()
    chess_board = chess.Board()
    clock = pygame.time.Clock()
    selected_square, selected_col, selected_row = None, None, None
    moved_col, moved_row = None, None
    selected, moved = False, False

    while True:
        clock.tick(SETTINGS["fps"])

        # Pulisci la finestra
        win.fill((255, 255, 255))  # Riempie la finestra con un colore di sfondo bianco

        # Usa Mediapipe per ottenere la posizione dell'indice
        x, y = get_index_finger_position()

        # Aggiornamento della scacchiera
        if selected:
            draw_board_with_highlight(win, selected_col, selected_row, "selection")
        elif moved:
            draw_board_with_highlight(win, moved_col, moved_row, "move")
        else:
            draw_board(win)        
        draw_pieces(win, chess_board)
            

        if x is not None and y is not None:                        
            # Calcola la riga e colonna in base alla posizione del dito
            row, col = (7 - y // 80), x // 80
            square = chess.square(col, row)

            
            # Disegna un puntatore rosso dove si trova l'indice
            pygame.draw.circle(win, SETTINGS["colors"]["pointer"], (x, y), radius=10)

            # Gestisci la selezione o il movimento sulla scacchiera
            if selected_square:
                move = chess.Move(selected_square, square)
                if move in chess_board.legal_moves:
                    moved_col, moved_row = handle_move(chess_board, move, col, 7 - row)
                    moved = True
                    selected_square = None
                    selected = False
                elif chess_board.piece_at(square):
                    selected_square, selected_col, selected_row = handle_selection(square, col, 7 - row)
                    selected = True
            elif chess_board.piece_at(square):
                selected_square, selected_col, selected_row = handle_selection(square, col, 7 - row)
                selected = True

        # Gestione eventi di uscita
        for event in pygame.event.get():            
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                hands.close()
                return
        

        pygame.display.update()

        # Verifica esito della partita
        if chess_board.outcome():
            print("La partita è finita:", chess_board.outcome())
            break


if __name__ == "__main__":
    main()
