import pygame
import chess

# Carica le immagini dei pezzi
PIECE_IMAGES = {}
for piece in ['P', 'R', 'N', 'B', 'Q', 'K', 'p', 'r', 'n', 'b', 'q', 'k']:
    PIECE_IMAGES[piece] = pygame.image.load(f"src/pieces/{piece}.png")

def draw_board(win):
    colors = [pygame.Color(235, 235, 208), pygame.Color(119, 148, 85)]
    
    square_size = 80
    for row in range(8):
        for col in range(8):
            color = colors[(row + col) % 2]
            pygame.draw.rect(win, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
    


def draw_board_with_highlight(win, highlight_col, highlight_row, highlight_type):
    # Disegna la scacchiera
    draw_board(win)
    
    # Definisci i colori per ciascun tipo di evidenziazione
    colors = {
        "selection": pygame.Color(200, 150, 90),  # Colore per la selezione
        "move": pygame.Color(200, 200, 60)        # Colore per la mossa
    }
    
    # Determina il colore in base al tipo di evidenziazione
    highlight_color = colors.get(highlight_type, pygame.Color(255, 255, 255))  # Default a bianco se non valido
    
    # Disegna il rettangolo evidenziato, se le coordinate sono fornite
    if highlight_col is not None and highlight_row is not None:
        square_size = 80
        pygame.draw.rect(win, highlight_color, pygame.Rect(highlight_col * square_size, highlight_row * square_size, square_size, square_size))

def draw_pieces(win, board):
    square_size = 80
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            x = (square % 8) * square_size
            y = (7 - square // 8) * square_size
            win.blit(PIECE_IMAGES[piece.symbol()], pygame.Rect(x, y, square_size, square_size))
