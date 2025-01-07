import pygame
import chess

class ChessBoardRenderer:
    # def validate_settings(settings):
    #     required_keys = ["is_white", "colors", "font", "square-size"]
    #     for key in required_keys:
    #         if key not in settings:
    #             raise ValueError(f"Missing required setting: {key}")

    def __init__(self, settings, piece_images):
        # validate_settings(settings) 
        self.is_white = settings["is_white"]
        self.colors = [settings["colors"]["light_square_pycolor"], settings["colors"]["dark_square_pycolor"]]
        self.font = pygame.font.SysFont(settings["font"]["name"], settings["font"]["size"])
        self.cursor_color = settings["colors"]["cursor"]
        self.square_size = settings["square-size"]
        self.piece_images = piece_images
        
        # Superficie per la scacchiera
        self.board_surface = pygame.Surface((self.square_size * 8, self.square_size * 8))
        self.create_board_surface()
        self.pieces_surface = None


    def create_board_surface(self):        
        for row in range(8):
            for col in range(8):
                pygame.draw.rect(self.board_surface, self.colors[(row + col) % 2], pygame.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size))
                row_label = 8 - row if self.is_white else row + 1
                col_label = chr(97 + col) if self.is_white else chr(104 - col)

                if col == 0:
                    label = self.font.render(str(row_label), True, self.colors[1 - ((row + col) % 2)])
                    self.board_surface.blit(label, (5, row * self.square_size + 5))

                if row == 7:
                    label = self.font.render(col_label, True, self.colors[1 - ((row + col) % 2)])
                    self.board_surface.blit(label, (col * self.square_size + 65, self.square_size * 8 - 20))                    
            
    def create_pieces_surface(self, board):   
        if not hasattr(self, 'square_size') or not self.square_size:
            raise ValueError("Errore: self.square_size non è definito o è 0.")
        if not hasattr(self, 'is_white'):
            raise ValueError("Errore: self.is_white non è definito.")
        if not self.piece_images:
            raise ValueError("Errore: self.piece_images è vuoto o non inizializzato.")
                     
        self.pieces_surface = pygame.Surface((self.square_size * 8, self.square_size * 8), pygame.SRCALPHA)
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square) if self.is_white else chess.square_rank(square)
                x, y = col * self.square_size, row * self.square_size
                if piece.symbol() not in self.piece_images:
                    print(f"Errore: immagine per il pezzo {piece.symbol()} non trovata.")
                    continue
                self.pieces_surface.blit(self.piece_images[piece.symbol()], (x, y))

    def update_pieces_surface(self, board):            
        if self.pieces_surface is None:
            self.create_pieces_surface(board)
        
        move = board.peek()

        start_square = move.from_square
        end_square = move.to_square

        start_col = chess.square_file(start_square)
        start_row = 7 - chess.square_rank(start_square) if self.is_white else chess.square_rank(start_square)
        end_col = chess.square_file(end_square)
        end_row = 7 - chess.square_rank(end_square) if self.is_white else chess.square_rank(end_square)

        start_color = self.colors[(start_row + start_col) % 2]
        end_color = self.colors[(end_row + end_col) % 2]

        # Ridisegna le celle coinvolte nell'ultima mossa
        pygame.draw.rect(self.pieces_surface, start_color, pygame.Rect(start_col * self.square_size, start_row * self.square_size, self.square_size, self.square_size))
        pygame.draw.rect(self.pieces_surface, end_color, pygame.Rect(end_col * self.square_size, end_row * self.square_size, self.square_size, self.square_size))

        # Ridisegna il pezzo sulla casella di arrivo
        piece = board.piece_at(end_square)
        if piece:
            piece_image = self.piece_images[piece.symbol()]
            self.pieces_surface.blit(piece_image, (end_col * self.square_size, end_row * self.square_size))


    def get_cursor_surface(self, cursor_pos):
        """
        Crea una superficie Pygame per rappresentare un cursore dinamico.
        """
        cursor_surface = pygame.Surface((self.square_size * 8, self.square_size * 8), pygame.SRCALPHA)
        pygame.draw.circle(cursor_surface, self.cursor_color, cursor_pos, 8)
        return cursor_surface

    def get_available_moves_surface(self, board, selected_square, color=(250, 100, 200, 128)):
        """
        Crea una superficie Pygame che rappresenta le mosse disponibili per il pezzo selezionato.
        """
        moves_surface = pygame.Surface((self.square_size * 8, self.square_size * 8), pygame.SRCALPHA)
        if selected_square is not None:
            for move in board.legal_moves:
                if move.from_square == selected_square:
                    to_square = move.to_square
                    col = chess.square_file(to_square)
                    row = 7 - chess.square_rank(to_square) if self.is_white else chess.square_rank(to_square)
                    center_x = col * self.square_size + self.square_size // 2
                    center_y = row * self.square_size + self.square_size // 2
                    pygame.draw.circle(moves_surface, color, (center_x, center_y), self.square_size // 6)
        return moves_surface


    # def draw_move_list(self, move_list, font, start_x, start_y, line_height=30):
    #     """
    #     Disegna l'elenco delle mosse giocate su una finestra Pygame.
    #     """

    #     for index, move in enumerate(move_list):
    #         move_text = font.render(f"{index + 1}. {move}", True, (0, 0, 0))  # Colore nero
    #         self.board_surface.blit(move_text, (start_x, start_y + index * line_height))

    # def draw_scrollable_moves(self, move_list, font, start_x, start_y, line_height, visible_lines, scroll_offset):
    #     """
    #     Disegna una lista di mosse con capacità di scorrimento.
    #     """
    #     max_visible = min(len(move_list), visible_lines)
    #     for i in range(max_visible):
    #         move_index = scroll_offset + i
    #         if move_index < len(move_list):
    #             move_text = font.render(f"{move_index + 1}. {move_list[move_index]}", True, (0, 0, 0))
    #             self.board_surface.blit(move_text, (start_x, start_y + i * line_height))

    # def draw_sidebar(self, win, remaining_time, move_list, position=(640, 10), width=160, height=640, font_size=24, scroll_offset=0):
    #     """
    #     Disegna la barra laterale accanto alla scacchiera, includendo il timer e la lista delle mosse.
    #     """
    #     # Disegna sfondo della barra
    #     pygame.draw.rect(win, (220, 220, 220), (position[0], 0, width, height))  # Sfondo grigio chiaro

    #     # Disegna il contorno della barra
    #     pygame.draw.rect(win, (0, 0, 0), (position[0], 0, width, height), 2)  # Bordo nero

    #     # Disegna il timer in alto
    #     font = pygame.font.Font(None, font_size)
    #     minutes = remaining_time // 60
    #     seconds = remaining_time % 60
    #     timer_text = f"{minutes:02}:{seconds:02}"
    #     timer_surface = font.render(f"Timer: {timer_text}", True, (255, 0, 0))
    #     win.blit(timer_surface, (position[0] + 10, position[1]))

    #     # Linea di separazione
    #     pygame.draw.line(win, (0, 0, 0), (position[0], 50), (position[0] + width, 50), 2)

    #     # Disegna la lista delle mosse
    #     move_list_start_y = 60  # Posizione di partenza della lista
    #     visible_lines = (height - move_list_start_y) // 30  # Numero di righe visibili, basato sull'altezza e sullo spazio disponibile
    #     self.draw_scrollable_moves(move_list, font, position[0] + 10, move_list_start_y, 30, visible_lines, scroll_offset)

    # def create_sidebar_surface(self, remaining_time, move_list, width=160, height=640, font_size=24, scroll_offset=0):
    #     """
    #     Crea una superficie Pygame per la barra laterale, includendo il timer e la lista delle mosse.
    #     """
    #     sidebar_surface = pygame.Surface((width, height))
    #     sidebar_surface.fill((220, 220, 220))  # Sfondo grigio chiaro

    #     # Disegna il contorno della barra
    #     pygame.draw.rect(sidebar_surface, (0, 0, 0), (0, 0, width, height), 2)  # Bordo nero

    #     # Disegna il timer in alto
    #     font = pygame.font.Font(None, font_size)
    #     minutes = remaining_time // 60
    #     seconds = remaining_time % 60
    #     timer_text = f"{minutes:02}:{seconds:02}"
    #     timer_surface = font.render(f"Timer: {timer_text}", True, (255, 0, 0))
    #     sidebar_surface.blit(timer_surface, (10, 10))

    #     # Linea di separazione
    #     pygame.draw.line(sidebar_surface, (0, 0, 0), (0, 50), (width, 50), 2)

    #     # Disegna la lista delle mosse
    #     move_list_start_y = 60  # Posizione di partenza della lista
    #     visible_lines = (height - move_list_start_y) // 30  # Numero di righe visibili, basato sull'altezza e sullo spazio disponibile
    #     self.draw_scrollable_moves(move_list, font, 10, move_list_start_y, 30, visible_lines, scroll_offset)

    #     return sidebar_surface
