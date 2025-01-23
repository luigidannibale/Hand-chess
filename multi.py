import pygame
import chess
import cv2
import threading
import queue
import os
import time
import chess.pgn

from hand_tracker import HandTracker
from hand_tracker import _get_board_layer



# class CountdownTimerThread:
#     def __init__(self, max_seconds, data_queue, stop_event):
#         """
#         Inizializza il thread per il countdown timer.
        
#         :param max_seconds: Durata massima del timer in secondi.
#         :param data_queue: Coda per comunicare con altri thread.
#         :param stop_event: Evento per fermare il thread.
#         """
#         self.max_seconds = max_seconds
#         self.data_queue = data_queue
#         self.stop_event = stop_event
#         self.thread = threading.Thread(target=self.run)
#         self.running = False

#     def start(self):
#         """Avvia il thread del timer."""
#         self.running = True
#         self.thread.start()

#     def run(self):
#         """Logica per eseguire il countdown timer e aggiornarlo in una finestra separata."""
#         pygame.init()
#         window_size = (200, 100)
#         window = pygame.display.set_mode(window_size)
#         pygame.display.set_caption("Countdown Timer")
#         font = pygame.font.Font(None, 48)
#         clock = pygame.time.Clock()

#         remaining_time = self.max_seconds
#         while self.running and remaining_time > 0 and not self.stop_event.is_set():
#             # Controlla eventi della finestra
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.stop_event.set()
#                     self.running = False

#             # Calcola minuti e secondi
#             minutes = remaining_time // 60
#             seconds = remaining_time % 60

#             # Mostra il timer
#             window.fill((0, 0, 0))  # Sfondo nero
#             timer_text = font.render(f"{minutes:02}:{seconds:02}", True, (255, 255, 255))
#             window.blit(timer_text, (window_size[0] // 2 - timer_text.get_width() // 2,
#                                      window_size[1] // 2 - timer_text.get_height() // 2))
#             pygame.display.flip()

#             # Aspetta un secondo
#             time.sleep(1)
#             remaining_time -= 1

#         # Notifica agli altri thread che il tempo è scaduto
#         if remaining_time <= 0:
#             self.data_queue.put(Thread_data(None, None, None, None, timer_running=False))
#             print("Tempo scaduto!")

#         pygame.quit()

#     def stop(self):
#         """Ferma il thread del timer."""
#         self.running = False
#         if self.thread.is_alive():
#             self.thread.join()

class Thread_data:
    def __init__(self, board_square = None, x = None, y = None, is_pinching = False, timer_running = False, update_display=False):
        self.board_square = board_square  # Rappresenta una casella sulla scacchiera        
        self.x = x  # Coordinata X della punta del dito indice
        self.y = y  # Coordinata Y della punta del dito indice
        self.is_pinching = is_pinching # Booleano che indica se i landmarks rilevano la pinch gesture 
        self.timer_running = timer_running  # Booleano che indica se il timer è in esecuzione
        self.update_display = update_display # Booleano che segnala se aggiornare il display

class BoardSquare:
    def __init__(self, square, col, row):
        self.square = square
        self.col = col
        self.row = row
    
    @staticmethod
    def from_coordinates(x, y, square_size=80):
        """Crea un oggetto BoardSquare dai pixel x e y."""
        if 0 <= x < square_size * 8 and 0 <= y < square_size * 8:
            row, col = (7 - y // square_size), x // square_size
            square = chess.square(col, row)
            return BoardSquare(square, col, row)
        return None  # Coordinate fuori dalla scacchiera

    @staticmethod
    def to_coordinates(square, square_size=80):
        """Converte una casella in coordinate pixel (x, y)."""
        col = chess.square_file(square)
        row = 7 - chess.square_rank(square)  # Scacchiera orientata verso il bianco
        return col * square_size, row * square_size

    def __repr__(self):
        return f"BoardSquare(square={self.square}, col={self.col}, row={self.row})"


def create_board_surface(settings):
    
    square_size = settings["square-size"]
    board_surface = pygame.Surface((square_size * 8, square_size * 8))
    font = pygame.font.SysFont(settings["font"]["name"], settings["font"]["size"])
    colors = [settings["colors"]["py_light"], settings["colors"]["py_dark"]]    
    
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(board_surface, color, 
                             pygame.Rect(col * square_size, row * square_size, square_size, square_size))
            
            # Disegna i numeri e le lettere
            if col == 0:  # Numeri (1-8) sul bordo sinistro
                label = font.render(str(8 - row), True, colors[((row + col) % 2 - 1)%2])
                board_surface.blit(label, (5, row * square_size + 5))
            if row == 7:  # Lettere (a-h) sul bordo inferiore
                label = font.render(chr(97 + col), True, colors[((row + col) % 2 - 1)%2])
                board_surface.blit(label, (col * square_size + 65, square_size * 8 - 20))
    return board_surface

def draw_pieces_surface(board,  PIECE_IMAGES, square_size=80):
    """
    Crea una superficie Pygame che rappresenta i pezzi attuali sulla scacchiera.

    Parametri:
    - board (chess.Board): L'oggetto scacchiera di python-chess con lo stato corrente.
    - square_size (int): La dimensione di ciascuna cella della scacchiera in pixel (default: 80).

    Ritorna:
    - pygame.Surface: La superficie con i pezzi posizionati correttamente.
    """

    pieces_surface = pygame.Surface((square_size * 8, square_size * 8), pygame.SRCALPHA)
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = 7 - chess.square_rank(square)  # Adatta per Pygame
            x, y = col * square_size, row * square_size
            pieces_surface.blit(PIECE_IMAGES[piece.symbol()], (x, y))
    return pieces_surface

def draw_cursor_surface(cursor_pos, square_size=80, color=(255, 0, 0)):
    """
    Crea una superficie Pygame per rappresentare un cursore dinamico.

    Parametri:
    - cursor_pos (tuple): Posizione corrente del cursore (x, y) in pixel.
    - square_size (int): La dimensione di ciascuna cella della scacchiera in pixel (default: 80).
    - color (tuple): Colore RGB del cursore (default: rosso).

    Ritorna:
    - pygame.Surface: La superficie con il cursore disegnato come un cerchio.
    """

    cursor_surface = pygame.Surface((square_size * 8, square_size * 8), pygame.SRCALPHA)    
    pygame.draw.circle(cursor_surface, color, cursor_pos, 8)
    return cursor_surface

def draw_available_moves_surface(board, selected_square, square_size=80, color=(250, 100, 200, 128)):
    """
    Crea una superficie Pygame che rappresenta le mosse disponibili per il pezzo selezionato.

    Parametri:
    - board (chess.Board): La scacchiera di gioco corrente.
    - selected_square (chess.Square): La posizione del pezzo selezionato.
    - square_size (int): Dimensione delle celle della scacchiera in pixel (default: 80).
    - color (tuple): Colore dei cerchi (RGBA con trasparenza).

    Ritorna:
    - pygame.Surface: Una superficie con cerchi nelle caselle delle mosse disponibili.
    """
    moves_surface = pygame.Surface((square_size * 8, square_size * 8), pygame.SRCALPHA)
    if selected_square is not None:
        # Ottieni le mosse disponibili per il pezzo selezionato
        for move in board.legal_moves:
            if move.from_square == selected_square:
                to_square = move.to_square
                col = chess.square_file(to_square)
                row = 7 - chess.square_rank(to_square)  # Coordinate ribaltate per Pygame
                center_x = col * square_size + square_size // 2
                center_y = row * square_size + square_size // 2
                pygame.draw.circle(moves_surface, color, (center_x, center_y), square_size // 6)
    return moves_surface

def update_move(pyframe, board, square_size=80):
    """
    Aggiorna la scacchiera ridisegnando solo le celle coinvolte nell'ultima mossa 
    e spostando il pezzo.

    Parametri:
    - pyframe (pygame.Surface): Superficie Pygame su cui disegnare.
    - board (chess.Board): Lo stato corrente della scacchiera.
    - square_size (int): Dimensione dei quadrati della scacchiera in pixel (default: 80).
    """
    light_color = pygame.Color(235, 235, 208)
    dark_color = pygame.Color(119, 148, 85)
    colors = [light_color, dark_color]

    # Ottieni l'ultima mossa
    move = board.peek()

    # Coordinate delle caselle di partenza e arrivo
    start_square = move.from_square
    end_square = move.to_square

    # Calcola colonna e riga per le caselle di partenza e arrivo
    start_col = chess.square_file(start_square)
    start_row = 7 - chess.square_rank(start_square)  # Adatta per il sistema Pygame
    end_col = chess.square_file(end_square)
    end_row = 7 - chess.square_rank(end_square)

    # Colori delle celle
    start_color = colors[(start_row + start_col) % 2]
    end_color = colors[(end_row + end_col) % 2]

    # Ridisegna la casella di partenza
    pygame.draw.rect(pyframe, start_color, pygame.Rect(start_col * square_size, start_row * square_size, square_size, square_size))

    # Ridisegna la casella di arrivo
    pygame.draw.rect(pyframe, end_color, pygame.Rect(end_col * square_size, end_row * square_size, square_size, square_size))

    # Ridisegna il pezzo sulla casella di arrivo
    piece = board.piece_at(end_square)
    if piece:
        piece_image = PIECE_IMAGES[piece.symbol()]
        pyframe.blit(piece_image, (end_col * square_size, end_row * square_size))
        
# #TODO: da fare surface
# def draw_timer(win, remaining_time, position=(10, 10), font_size=48, color=(255, 0, 0)):
#     """
#     Disegna il timer nella finestra di gioco.

#     :param win: La finestra di Pygame.
#     :param remaining_time: Tempo rimanente in secondi.
#     :param position: Posizione del timer sulla finestra.
#     :param font_size: Dimensione del font del timer.
#     :param color: Colore del testo del timer.
#     """
#     font = pygame.font.Font(None, font_size)
#     minutes = remaining_time // 60
#     seconds = remaining_time % 60
#     timer_text = f"{minutes:02}:{seconds:02}"
#     text_surface = font.render(timer_text, True, color)
#     win.blit(text_surface, position)

#TODO: da fare unica classe oppure surface addetta
#{
# def draw_move_list(pyframe, move_list, font, start_x, start_y, line_height=30):
    """
    Disegna l'elenco delle mosse giocate su una finestra Pygame.
    - pyframe: La finestra Pygame.
    - move_list: Lista di mosse giocate (es. ["e2e4", "e7e5", "g1f3"]).
    - font: Font da utilizzare per il rendering del testo.
    - start_x, start_y: Coordinate di partenza per il disegno del testo.
    - line_height: Distanza verticale tra le righe.
    """
    for index, move in enumerate(move_list):
        move_text = font.render(f"{index + 1}. {move}", True, (0, 0, 0))  # Colore nero
        pyframe.blit(move_text, (start_x, start_y + index * line_height))

def draw_scrollable_moves(pyframe, move_list, font, start_x, start_y, line_height, visible_lines, scroll_offset):
    """
    Disegna una lista di mosse con capacità di scorrimento.
    - pyframe: La finestra Pygame.
    - move_list: Lista di mosse giocate (es. ["e2e4", "e7e5", "g1f3"]).
    - font: Font da utilizzare per il rendering del testo.
    - start_x, start_y: Coordinate di partenza per il disegno del testo.
    - line_height: Distanza verticale tra le righe.- visible_lines: Numero massimo di righe visibili.
    - scroll_offset: Indice della prima mossa da mostrare.
    """
    max_visible = min(len(move_list), visible_lines)
    for i in range(max_visible):
        move_index = scroll_offset + i
        if move_index < len(move_list):
            move_text = font.render(f"{move_index + 1}. {move_list[move_index]}", True, (0, 0, 0))
            pyframe.blit(move_text, (start_x, start_y + i * line_height))

#TODO: da fare surface
def draw_sidebar(win, remaining_time, move_list, position=(640, 10), width=160, height=640, font_size=24, scroll_offset=0):
    """
    Disegna la barra laterale accanto alla scacchiera, includendo il timer e la lista delle mosse.

    :param win: La finestra di Pygame.
    :param remaining_time: Tempo rimanente in secondi.
    :param move_list: Lista delle mosse giocate.
    :param position: Posizione di partenza della barra laterale.
    :param width: Larghezza della barra.
    :param height: Altezza della barra.
    :param font_size: Dimensione del font del testo.
    :param scroll_offset: Indice di scorrimento della lista delle mosse.
    """
    # Disegna sfondo della barra
    pygame.draw.rect(win, (220, 220, 220), (position[0], 0, width, height))  # Sfondo grigio chiaro

    # Disegna il contorno della barra
    pygame.draw.rect(win, (0, 0, 0), (position[0], 0, width, height), 2)  # Bordo nero

    # Disegna il timer in alto
    font = pygame.font.Font(None, font_size)
    minutes = remaining_time // 60
    seconds = remaining_time % 60
    timer_text = f"{minutes:02}:{seconds:02}"
    timer_surface = font.render(f"Timer: {timer_text}", True, (255, 0, 0))
    win.blit(timer_surface, (position[0] + 10, position[1]))

    # Linea di separazione
    pygame.draw.line(win, (0, 0, 0), (position[0], 50), (position[0] + width, 50), 2)

    # Disegna la lista delle mosse
    move_list_start_y = 60  # Posizione di partenza della lista
    visible_lines = (height - move_list_start_y) // 30  # Numero di righe visibili, basato sull'altezza e sullo spazio disponibile
    draw_scrollable_moves(win, move_list, font, position[0] + 10, move_list_start_y, 30, visible_lines, scroll_offset)
#}




def hand_tracking_thread(cap, tracker, data_queue, stop_event, board_size=640, square_size=80):
    """
    Thread per il tracciamento della mano, invia le coordinate tramite una coda.
    """
    def get_square_from_position(x, y, frame_width, frame_height, square_size=40):
        if not (80 <= x <= 400 and 80 <= y <= 400):
            return None, None
        col = 2 * (x - 80) // square_size
        row = 7 - (2 * (y - 80) // square_size)
        return int(row), int(col)

    frame_width = frame_height = 540
    board_layer = _get_board_layer(frame_width,frame_height,40,(80,80),(255,0,0),3)
    
    while not stop_event.is_set():
        ret, frame = cap.read()
        
        if not ret:
            print("Errore nel catturare il frame.")
            continue

        frame = cv2.flip(frame, 1)
        
        frame = cv2.resize(frame, (frame_width, frame_height))
        frame = tracker.process_frame(frame)
        #frame = cv2.addWeighted(frame, 1, board_layer, 1, 0)

        if tracker.hand_landmarks:            
            x = int(tracker.hand_landmarks.landmark[8].x * frame_height)  # Indice
            y = int(tracker.hand_landmarks.landmark[8].y * frame_width)                        
            
            row, col = get_square_from_position(x, y, frame_width, frame_height, square_size)
            if row != None and col != None:
                board_square = BoardSquare(chess.square(col, row), col, row)                
                is_pinching = tracker.is_pinching(tracker.hand_landmarks)  # Rileva il gesto di pinching
                data_queue.put(Thread_data(board_square, 2*x-80, 2*y-80, is_pinching))
        
        cv2.imshow("Hand Tracking", frame)
        cv2.moveWindow("Hand Tracking", 800, 40)
            
    cap.release()
    cv2.destroyAllWindows()
    stop_event.set()

def initialize_game():
    """
    Inizializza la finestra di Pygame.
    """
    
    return win, SETTINGS

def save_game(chess_board, move_list, file_path="game.pgn"):
    """
    Salva la partita corrente in un file PGN.

    :param chess_board: La scacchiera corrente.
    :param move_list: La lista delle mosse giocate.
    :param file_path: Il percorso del file dove salvare la partita.
    """
    with open(file_path, "w") as f:
        game = chess.pgn.Game()  # Crea una nuova partita
        node = game

        # Aggiungi le mosse alla partita
        for move in move_list:
            node = node.add_variation(chess.Move.from_uci(move))

        # Salva la partita nel file
        f.write(game.accept(chess.pgn.StringExporter()))
    print(f"Partita salvata in {file_path}")

def load_game(file_path="game.pgn"):
    """
    Carica una partita da un file PGN.

    :param file_path: Il percorso del file da cui caricare la partita.
    :return: (chess.Board, list) - La scacchiera caricata e la lista delle mosse.
    """
    if not os.path.exists(file_path):
        print(f"File {file_path} non trovato.")
        return None, []

    with open(file_path, "r") as f:
        game = chess.pgn.read_game(f)  # Legge la partita dal file PGN

    board = chess.Board()  # Inizializza una nuova scacchiera
    move_list = []

    # Itera sulle mosse della partita
    for node in game.mainline():
        move = node.move  # Estrai la mossa dal nodo
        if move:  # Assicurati che la mossa non sia None
            board.push(move)
            move_list.append(move.uci())  # Aggiungi la mossa alla lista delle mosse

    print(f"Partita caricata da {file_path}")
    return board, move_list


# Aggiorna la funzione `game_thread` per includere salvataggio e caricamento
def game_thread(data_queue, stop_event, win, SETTINGS, max_game_time):
    clock = pygame.time.Clock()
    chess_board = chess.Board()
    selected_square = None
    

    start_time = time.time()  # Momento di inizio del timer
    remaining_time = max_game_time

    move_list = []  # Lista delle mosse giocate
    scroll_offset = 0  # Offset per lo scrolling della lista delle mosse

    # Disegna la finestra di gioco
    win.fill((255, 255, 255))
    board_surface = create_board_surface(SETTINGS)          # Layer 1: Scacchiera statica


    PIECE_IMAGES = {}
    PIECE_PATH = "src/pieces/"

    try:
        for piece in ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k']:
            PIECE_IMAGES[piece] = pygame.image.load(os.path.join(PIECE_PATH, f"{piece}.png"))
    except FileNotFoundError as e:
        print(f"Errore: Impossibile trovare l'immagine del pezzo: {e}")
        exit()
    pieces_surface = draw_pieces_surface(chess_board, PIECE_IMAGES)   # Layer 2: Pezzi sulla scacchiera
    previous_available_moves_surface = available_moves_surface = None # Layer 4: Mosse disponibili
    win.blit(board_surface, (0, 0))   # Scacchiera statica
    win.blit(pieces_surface, (0, 0))  # Pezzi                            
    data_queue.put(Thread_data(None,None,None,None,None,None,True))
    cursor_surface = None  # Initialize cursor_surface

    while not stop_event.is_set():
        clock.tick(SETTINGS["fps"])
        
        # Calcola il tempo rimanente
        elapsed_time = time.time() - start_time
        remaining_time = max(0, max_game_time - int(elapsed_time))

        # Se il tempo è scaduto, invia un segnale nella coda e ferma il gioco
        if remaining_time <= 0:
            print("Tempo scaduto!")
            data_queue.put(Thread_data())
            stop_event.set()
            break
        
        win.blit(board_surface, (0, 0))   # Scacchiera statica
        win.blit(pieces_surface, (0, 0))  # Pezzi  

        # # Disegna la barra laterale con il timer e la lista delle mosse
        # draw_sidebar(win, remaining_time, move_list, scroll_offset=scroll_offset)
        pygame.display.update()
  
        
        # Controlla i dati dalla coda
        # Dentro il while principale, aggiorna quando un pezzo viene selezionato
        if not data_queue.empty():
            try:
                T_data = data_queue.get_nowait()
                cursor_surface = draw_cursor_surface((T_data.x - 80, T_data.y - 80), 80, SETTINGS["colors"]["cursor"])  # Layer 3: Cursore
                
                # Click gesture rilevato
                if T_data.is_pinching:                                        
                    if selected_square is None: # Selezione del pezzo
                        selected_square = T_data.board_square.square
                        available_moves_surface = draw_available_moves_surface(chess_board, selected_square, 80)  # Layer 4: Mosse
                    
                    else: # Tentativo di eseguire una mossa                        
                        move = chess.Move(selected_square, T_data.board_square.square)
                        
                        if move in chess_board.legal_moves: # Esegue la mossa"                            
                            chess_board.push(move)
                            move_list.append(move.uci())
                            update_move(win, chess_board)
                            pieces_surface = draw_pieces_surface(chess_board, PIECE_IMAGES)  # Aggiorna i pezzi
                            print(f"Mossa eseguita: {move.uci()}")
                            selected_square = None
                            previous_available_moves_surface = available_moves_surface = None  # Rimuovi il layer delle mosse
                                                
                        elif selected_square != T_data.board_square.square: # Selezione di un altro pezzo"                            
                            selected_square = T_data.board_square.square
                            previous_available_moves_surface = available_moves_surface
                            available_moves_surface = draw_available_moves_surface(chess_board, selected_square, 80)  # Layer 4: Mosse
                                                
                        elif selected_square == T_data.board_square.square: # Riselezione dello stesso pezzo"                            
                            previous_available_moves_surface = available_moves_surface
                            continue
                                                    
                # Disegna tutti i layer
                win.blit(board_surface, (0, 0))          # Layer 1: Scacchiera
                win.blit(pieces_surface, (0, 0))         # Layer 2: Pezzi
                if available_moves_surface is not None:  # Layer 4: Mosse disponibili
                    win.blit(available_moves_surface, (0, 0))
                if cursor_surface is not None:           # Layer 3: Cursore
                    win.blit(cursor_surface, (0, 0))
                pygame.display.update()
            except queue.Empty:
                pass

        # Gestisci eventi Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_event.set()
                elif event.key == pygame.K_UP:  # Scorri la lista delle mosse verso l'alto
                    scroll_offset = max(0, scroll_offset - 1)                
                elif event.key == pygame.K_DOWN:  # Scorri la lista delle mosse verso il basso
                    max_scroll = max(0, len(move_list) - (640 - 60) // 30)
                    scroll_offset = min(max_scroll, scroll_offset + 1)
                elif event.key == pygame.K_m:  # Scorri la lista delle mosse verso l'alto
                    tracker.landmarks_activated = not tracker.landmarks_activated 
                elif event.key == pygame.K_s:  # Salva la partita
                    save_game(chess_board, move_list)
                elif event.key == pygame.K_l:  # Carica una partita
                    chess_board, move_list = load_game()                    
                    pieces_surface = draw_pieces_surface(chess_board, PIECE_IMAGES)   # Layer 2: Pezzi sulla scacchiera
                    previous_available_moves_surface = None
                    start_time = time.time()  # Reset del timer al momento del caricamento
                    remaining_time = max_game_time
            pygame.display.update()


        


if __name__ == "__main__":

    os.environ["SDL_VIDEODRIVER"] = "x11"
    os.environ["SDL_RENDER_DRIVER"] = "software"
    os.environ['SDL_VIDEO_WINDOW_POS'] = f"{0},{40}"

    
    # Costanti
    WIDTH, HEIGHT = 640, 640
    SQUARE_SIZE = WIDTH // 8
    FONT_SIZE = 20

    # Colori
    LIGHT_COLOR = pygame.Color(235, 235, 208)
    DARK_COLOR = pygame.Color(119, 148, 85)
    CURSOR_COLOR = (255, 0, 0)  # Rosso per il cursore
    
    
    stop_event = threading.Event()  # Variabile per fermare i thread        
    data_queue = queue.Queue()  # Coda per la comunicazione tra thread

    tracker = HandTracker()  # Inizializza il tracciatore e la videocamera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Errore nell'aprire la videocamera.", SystemError)
        exit()

    PIECE_IMAGES = {}
    PIECE_PATH = "img/pieces/"
    
    SETTINGS = {
        "width": 800,  # Larghezza aumentata per includere la barra laterale
        "height": 640,
        "fps": 60,
        "colors": {
            "selection": (0, 204, 0),
            "move": (200, 200, 60),
            "cursor": (255, 0, 0),
        }
    }

    try:
        for piece in ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k']:
            PIECE_IMAGES[piece] = pygame.image.load(os.path.join(PIECE_PATH, f"{piece}.png"))
    except FileNotFoundError as e:
        print(f"Errore: Impossibile trovare l'immagine del pezzo: {e}")
        exit()

    pygame.init()
    pygame.display.init()
    
    win = pygame.display.set_mode((SETTINGS["width"], SETTINGS["height"]), pygame.RESIZABLE)
    pygame.display.set_caption("Chess Game")


    # Imposta il timer massimo (es. 300 secondi = 5 minuti)
    max_game_time = 300

    # Crea i thread
    thread1 = threading.Thread(target=hand_tracking_thread, args=(cap, tracker, data_queue, stop_event))
    thread2 = threading.Thread(target=game_thread, args=(data_queue, stop_event, win, SETTINGS, max_game_time))

    # Avvia i thread
    thread1.start()
    thread2.start()

    # Aspetta che i thread terminino
    thread1.join()
    thread2.join()
