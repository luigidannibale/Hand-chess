import pygame
import chess
import cv2
import threading
import queue
import os
from hand_tracker import HandTracker
from board import draw_board, draw_pieces, draw_board_with_highlight, BoardSquare

def get_square_from_position(x, y, frame_width, frame_height, board_size=640, square_size=80):
    """
    Mappa le coordinate della videocamera alle coordinate della scacchiera.
    """
    x_norm = x / frame_width
    y_norm = y / frame_height

    x_proj = x_norm * board_size
    y_proj = y_norm * board_size

    col = int(x_proj // square_size)
    row = int(y_proj // square_size)

    row = 7 - row  # Inverti riga per orientamento scacchiera
    return row, col

def hand_tracking_thread(cap, tracker, data_queue, stop_event, board_size=640, square_size=80):
    """
    Thread per il tracciamento della mano, invia le coordinate tramite una coda.
    """
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Errore nel catturare il frame.")
            continue

        frame = cv2.flip(frame, 1)
        frame = tracker.process_frame(frame)

        if tracker.hand_landmarks:
            x = int(tracker.hand_landmarks.landmark[8].x * frame.shape[1])
            y = int(tracker.hand_landmarks.landmark[8].y * frame.shape[0])
            
            row, col = get_square_from_position(x, y, frame_width, frame_height, board_size, square_size)

            board_square = BoardSquare(chess.square(col, row), col, row)
            data_queue.put((board_square, x, y, tracker.is_pinching(tracker.hand_landmarks)))

        cv2.imshow("Hand Tracking", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    stop_event.set()

def initialize_game():
    """
    Inizializza la finestra di Pygame.
    """
    SETTINGS = {
        "width": 640,
        "height": 640,
        "fps": 60,
        "colors": {
            "selection": (0, 204, 0),
            "move": (200, 200, 60),
            "cursor": (255, 0, 0),
        }
    }

    pygame.init()
    pygame.display.init()
    win = pygame.display.set_mode((SETTINGS["width"], SETTINGS["height"]), pygame.RESIZABLE)
    pygame.display.set_caption("Chess Game")
    return win, SETTINGS

def game_thread(data_queue, stop_event):
    """
    Thread principale del gioco che gestisce il rendering e le mosse.
    """
    win, SETTINGS = initialize_game()
    clock = pygame.time.Clock()

    chess_board = chess.Board()
    selected_square = None
    selected = False

    while not stop_event.is_set():
        clock.tick(SETTINGS["fps"])

        win.fill((255, 255, 255))

        if selected and selected_square:
            draw_board_with_highlight(win, selected_square.col, selected_square.row, SETTINGS["colors"]["selection"])
        else:
            draw_board(win)

        draw_pieces(win, chess_board)

        # Controlla i dati dalla coda
        if not data_queue.empty():
            board_square, x, y, is_pinching = data_queue.get()
            pygame.draw.circle(win, SETTINGS["colors"]["cursor"], (x, y), 10)

            if is_pinching:
                if selected_square is None:
                    selected_square = board_square
                    selected = True
                else:
                    move = chess.Move(selected_square.square, board_square.square)
                    if move in chess_board.legal_moves:
                        chess_board.push(move)
                        print(f"Mossa eseguita: {move.uci()}")
                    selected_square = None
                    selected = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_event.set()

        pygame.display.update()

if __name__ == "__main__":
    os.environ["SDL_VIDEODRIVER"] = "x11"

    # Variabile per fermare i thread
    stop_event = threading.Event()

    # Coda per la comunicazione tra thread
    data_queue = queue.Queue()

    # Inizializza il tracciatore e la videocamera
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Errore nell'aprire la videocamera.")
        exit()


    # Crea i thread
    thread1 = threading.Thread(target=hand_tracking_thread, args=(cap, tracker, data_queue, stop_event))
    #thread2 = threading.Thread(target=game_thread, args=(data_queue, stop_event))

    # Avvia i thread
    thread1.start()
    #thread2.start()
    game_thread(data_queue, stop_event)
    # Aspetta che i thread terminino
    thread1.join()
    #thread2.join()

    print("Programma terminato.")
