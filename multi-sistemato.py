import pygame
import chess
import cv2
import threading
import queue
import os
import numpy as np

from chessboard_renderer import ChessBoardRenderer

from hand_tracker import HandTracker
from hand_tracker import _get_board_layer

from enum import Enum, auto

class DataType(Enum):
    BOARD_FRAME = auto()    
    CAM_FRAME = auto()
    HAND_DATA = auto()
    SIG_ABORT = auto()


# Definizione del thread di tracciamento delle mani
def hand_tracking_thread(cap, tracker, data_queue, w, h , board_size=640, square_size=80):    
    class HandData:
        def __init__(self, board_square=None, x=None, y=None, is_pinching=False):
            self.board_square = board_square
            self.x = x
            self.y = y
            self.is_pinching = is_pinching


    def get_square_from_position(x, y, frame_width, frame_height, offset_x=80, offset_y=80, square_size=40):
        if not (offset_x <= x <= offset_x + 8 * square_size and offset_y <= y <= offset_y + 8 * square_size):
            return None, None        
        col = (x - offset_x) // square_size
        row = 7 - (y - offset_y) // square_size  # Invertiamo la riga (scacchiera rovesciata)
        return int(row), int(col)
    
    board_layer = _get_board_layer(w, h, 40, (80, 80), (255, 0, 0), 3)
    while cap.isOpened():
        ret, frame = cap.read()        
        if not ret:
            print("Errore nel catturare il frame.")
            continue        
        frame = cv2.resize(frame, (w, h))
        frame, is_pinching = tracker.process_frame(frame)
        frame = cv2.addWeighted(frame, 1, board_layer, 1, 0)
        frame = cv2.flip(frame, 1)    
        if is_pinching:
            cv2.putText(frame, "Pinching!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        if tracker.hand_landmarks:            
            x = int((1 - tracker.hand_landmarks.landmark[8].x) * w)  # Indice (adjusted for flipped frame)
            y = int(tracker.hand_landmarks.landmark[8].y * h)                                    
            row, col = get_square_from_position(x, y, w, h)
            if row != None and col != None:
                board_square = chess.square(col, row)
                hand_data = HandData(board_square, x, y, is_pinching)
                data_queue.put((DataType.HAND_DATA, hand_data))  # Passiamo i dati al thread principale
        data_queue.put((DataType.CAM_FRAME, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))  # Inviamo il frame al thread principale
        cv2.waitKey(1)  # Aggiungi waitKey per garantire che la finestra venga aggiornata        
    
    cap.release()
    cv2.destroyAllWindows()    
    data_queue.put(DataType.SIG_ABORT,None)  # Segnale che questo thread sta terminando

def game_thread(data_queue, stop_event, renderer, screen, settings, model_board):
    assert isinstance(renderer, ChessBoardRenderer)
    assert isinstance(screen, pygame.Surface)
    clock = pygame.time.Clock()
    cursor_surface = None
    available_moves_surface = None
    selected_square = None
    
    print("Game thread started")
    
    # Disegna la scacchiera
    renderer.create_board_surface()
    screen.blit(renderer.board_surface, (0, 0))

    print("Scacchiera disegnata")

    # Disegna i pezzi
    
    renderer.create_pieces_surface(model_board)
    if renderer.pieces_surface is not None:
        screen.blit(renderer.pieces_surface, (0, 0))
        print("Pezzi disegnati")
    else:
        print("Errore: pieces_surface è None")

    while not stop_event.is_set():                
        if not data_queue.empty():
            data_type, data = data_queue.get()
            if data_type == DataType.HAND_DATA:
                cursor_surface = renderer.get_cursor_surface((data.x - 80, data.y - 80))
                if data.is_pinching:
                    if selected_square is None:
                        selected_square = data.board_square
                        available_moves_surface = renderer.get_available_moves_surface(model_board, selected_square)
                    else:
                        move = chess.Move(selected_square, data.board_square)
                        if move in model_board.legal_moves:
                            model_board.push(move)
                            selected_square = None
                            available_moves_surface = None
                            renderer.update_pieces_surface(model_board)
                            if renderer.pieces_surface is not None:
                                screen.blit(renderer.pieces_surface, (0, 0))
                                print("Pezzi aggiornati")
                            else:
                                print("Errore: pieces_surface è None dopo l'aggiornamento")
                        else:
                            selected_square = data.board_square
                            available_moves_surface = renderer.get_available_moves_surface(model_board, selected_square)

        if cursor_surface is not None:
            screen.blit(cursor_surface, (0, 0))
        if available_moves_surface is not None:
            screen.blit(available_moves_surface, (0, 0))

        #pygame.display.flip()

# Funzione principale
def main():
    os.environ["SDL_VIDEODRIVER"] = "x11"

    cam_height = cam_wiidth = 540
    board_width = 640
    sidebar_width = 100  # Set sidebar width to 0
    WIDTH = cam_wiidth + board_width + sidebar_width
    HEIGHT = board_height  = sidebar_height = 640

    pygame.init()
    screen_info = pygame.display.Info()

    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{(screen_info.current_w-WIDTH)//2},{(screen_info.current_h-HEIGHT)//2}"
    print(os.environ['SDL_VIDEO_WINDOW_POS'])

    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
    
    pygame.display.set_caption("Test Pygame Window")

    SETTINGS = {                
        "colors": {
            # "selection": (0, 204, 0),
            # "move": (200, 200, 60),
            "cursor": (255, 0, 0),
            "light_square_pycolor":pygame.Color(235, 235, 208),
            "dark_square_pycolor":pygame.Color(119, 148, 85),
        },
        "square-size":80,
        "font":{
            "name":"arial",
            "size":20
        },
        "is_white":True,                
    }

    model_board = chess.Board()
    PIECE_IMAGES = {}
    PIECE_PATH = "src/pieces/"

    try:
        for piece in ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k']:
            PIECE_IMAGES[piece] = pygame.image.load(os.path.join(PIECE_PATH, f"{piece}.png"))
        print("PIECE_IMAGES caricato correttamente")
    except FileNotFoundError as e:
        print(f"Errore: Impossibile trovare l'immagine del pezzo: {e}")
        exit()

    boardRenderer = ChessBoardRenderer(SETTINGS, PIECE_IMAGES)

    # Crea una coda per comunicare con il thread di tracciamento delle mani
    data_queue = queue.Queue()

    # Crea il tracker delle mani
    tracker = HandTracker()

    # Crea il thread di tracciamento delle mani e lo avvia come daemon
    cap = cv2.VideoCapture(0)  # Usa la videocamera predefinita
    hand_thread = threading.Thread(target=hand_tracking_thread, args=(cap, tracker, data_queue, cam_wiidth, cam_height), daemon=True)
    hand_thread.start()

    # Crea e avvia il thread del renderer
    g_thread = threading.Thread(target=game_thread, args=(data_queue, stop_event, boardRenderer, screen, SETTINGS, model_board), daemon=True)
    g_thread.start()

    while not stop_event.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_event.set()

        # Recupera i dati dalla coda del thread di tracciamento delle mani
        if not data_queue.empty():
            data_type, data = data_queue.get()

            if data_type == DataType.SIG_ABORT:  # Fine del thread di tracciamento delle mani
                break

            if data_type == DataType.CAM_FRAME:  # Se è un frame                                
                screen.blit(pygame.image.fromstring(data.tobytes(), data.shape[1::-1], 'RGB'), (WIDTH - cam_wiidth, (HEIGHT - cam_height)//2))  # Mostra il frame nella finestra
                pygame.display.update()
        
        pygame.display.flip()

    cap.release()
    pygame.quit()

if __name__ == "__main__":
    stop_event = threading.Event()
    main()
