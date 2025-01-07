import pygame
import chess
from board import draw_board, draw_pieces, draw_board_with_highlight
from board import BoardSquare
import os

def handle_selection(board_square):
    """Gestisce la selezione di un pezzo."""
    print("Hai selezionato:", chess.square_name(board_square.square))
    return board_square

def handle_move(chess_board, move, board_square):
    """Gestisce la mossa di un pezzo."""
    chess_board.push(move)
    print(f"Mossa eseguita: {move.uci()}")
    return board_square

def initialize_game():
    """Inizializza la finestra di Pygame."""
    SETTINGS = {
        "width": 640,
        "height": 640,
        "fps": 60,
        "colors": {
            "selection": (0, 204, 0),
            "move": (200, 200, 60),
        }
    }

    pygame.init()
    pygame.display.init()
    
    win = pygame.display.set_mode((SETTINGS["width"], SETTINGS["height"]), pygame.RESIZABLE)
    pygame.display.set_caption("Chess Game")
    return win, SETTINGS

def _main():
    
    win, SETTINGS = initialize_game()
    clock = pygame.time.Clock()

    chess_board = chess.Board()  # Crea la scacchiera iniziale
    selected_square = None
    moved_square = None
    selected = False
    moved = False

    while True:
        clock.tick(SETTINGS["fps"])

        # Pulisci la finestra e disegna la scacchiera
        win.fill((255, 255, 255))  # Sfondo bianco

        if selected and selected_square:
            draw_board_with_highlight(win, selected_square.col, selected_square.row, SETTINGS["colors"]["selection"])
        elif moved and moved_square:
            draw_board_with_highlight(win, moved_square.col, moved_square.row, SETTINGS["colors"]["move"])
        else:
            draw_board(win)

        draw_pieces(win, chess_board)

        # Gestione eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos

                # Ottieni il BoardSquare dal clic
                board_square = BoardSquare.from_coordinates(mouse_x, mouse_y)

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

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return

        pygame.display.update()

        # Verifica esito della partita
        if chess_board.outcome():
            print("La partita è finita:", chess_board.outcome())
            break

if __name__ == "__main__":
    #os.environ["SDL_VIDEODRIVER"] = "wayland"
    _main()
