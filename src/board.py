import pygame
import chess
import os

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

def draw_board(win, square_size=80):
    light_color = pygame.Color(235, 235, 208)  # Colore chiaro
    dark_color = pygame.Color(119, 148, 85)   # Colore scuro
    colors = [light_color, dark_color]
    
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
    
def draw_board_with_highlight(win, highlight_col=None, highlight_row=None, highlight_color=(0, 204, 0), square_size=80):
    # Disegna la scacchiera
    draw_board(win, square_size)
    
    # Evidenzia una casella specifica, se le coordinate sono valide
    if highlight_col is not None and highlight_row is not None:
        if 0 <= highlight_col < 8 and 0 <= highlight_row < 8:
            pygame.draw.rect(win, highlight_color, pygame.Rect(
                highlight_col * square_size, 
                (7 - highlight_row) * square_size, 
                square_size, 
                square_size
            ))

def draw_pieces(win, board, square_size=80, white=True):
    """Disegna i pezzi sulla scacchiera."""
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            col = chess.square_file(square)
            row = chess.square_rank(square) if not white else (7 - chess.square_rank(square))
            x, y = col * square_size, row * square_size
            win.blit(PIECE_IMAGES[piece.symbol()], pygame.Rect(x, y, square_size, square_size))


PIECE_IMAGES = {}
PIECE_PATH = "img/pieces/"

try:
    for piece in ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k']:
        PIECE_IMAGES[piece] = pygame.image.load(os.path.join(PIECE_PATH, f"{piece}.png"))
except FileNotFoundError as e:
    print(f"Errore: Impossibile trovare l'immagine del pezzo: {e}")
    exit()
