import pygame
import cv2
import threading
import queue
import os
import game_v2


from hand_tracker import HandTracker
from hand_tracker import hand_tracking_thread

def show_popup(screen,options,WIDTH,HEIGHT):
    # Colori
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREY = (200, 200, 200)
    BLUE = (0, 0, 255)
    font = pygame.font.Font(None, 36)


    popup_width, popup_height = 300, 200
    popup_x = (WIDTH - popup_width) // 2
    popup_y = (HEIGHT - popup_height) // 2
    
    selected_option = 0  # Indice della selezione iniziale

    # Ciclo del popup
    popup_running = True
    while popup_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                # Controlla se l'utente ha cliccato sui radio button
                for i, option in enumerate(options):
                    button_x = popup_x + 20
                    button_y = popup_y + 50 + i * 40
                    if (mouse_x - button_x) ** 2 + (mouse_y - button_y) ** 2 <= 10 ** 2:
                        selected_option = i

                # Controlla se l'utente ha cliccato su "OK"
                ok_button_rect = pygame.Rect(popup_x + popup_width // 2 - 50, popup_y + popup_height - 60, 100, 40)
                if ok_button_rect.collidepoint(mouse_x, mouse_y):
                    popup_running = False  # Esci dal popup

        # Disegna il popup
        pygame.draw.rect(screen, GREY, (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(screen, BLACK, (popup_x, popup_y, popup_width, popup_height), 2)

        # Disegna i radio button
        for i, option in enumerate(options):
            button_x = popup_x + 20
            button_y = popup_y + 50 + i * 40
            pygame.draw.circle(screen, BLACK, (button_x, button_y), 10, 2)
            if i == selected_option:
                pygame.draw.circle(screen, BLUE, (button_x, button_y), 6)

            text = font.render(f"{option}", True, BLACK)
            screen.blit(text, (button_x + 30, button_y - 15))

        # Disegna il pulsante "OK"
        ok_button_rect = pygame.Rect(popup_x + popup_width // 2 - 50, popup_y + popup_height - 60, 100, 40)
        pygame.draw.rect(screen, BLUE, ok_button_rect)
        ok_text = font.render("OK", True, WHITE)
        screen.blit(ok_text, (ok_button_rect.x + 30, ok_button_rect.y + 5))

        pygame.display.flip()
        screen.fill(WHITE)  # Resetta lo schermo principale

    return options[selected_option]


if __name__ == "__main__":
    os.environ["SDL_VIDEODRIVER"] = "x11"
    
    stop_event = threading.Event()  # Variabile per fermare i thread        
    data_queue = queue.Queue()  # Coda per la comunicazione tra thread
    
    available_cams = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cams.append(i)            
        cap.release()
    # TODO: Implementare la scelta della videocamera
    # if not available_cams:
    #     print("Nessuna videocamera disponibile.", SystemError)
    #     exit()
    # # Chiedi all'utente di scegliere una videocamera
    # print("Videocamere disponibili:")
    # for i, cam in enumerate(available_cams):
    #     print(f"{i}: Camera {cam}")
    #cam_index = int(input("Scegli la videocamera da utilizzare (inserisci il numero): "))
    # if cam_index < 0 or cam_index >= len(available_cams):
    #     print("Scelta non valida.", ValueError)
    #     exit()
    WIDTH = HEIGHT = 480
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Scegli la videocamera")
    pygame.display.set_icon(pygame.image.load("img/pieces/P.png"))
    selected_cam = show_popup(screen, available_cams,WIDTH,HEIGHT)    
    pygame.quit()
    print(f"Hai selezionato {selected_cam}")
    
    
    cap = cv2.VideoCapture(selected_cam)
    if not cap.isOpened():
        print("Errore nell'aprire la videocamera.", SystemError)
        exit()

    PIECE_PATH = "img/pieces/"    
    SETTINGS = {      
        "width": 800,  # Larghezza aumentata per includere la barra laterale
        "height": 640,
        "fps": 60,                  
        "colors": {
            "selection": (0, 204, 0),
            "move": (200, 200, 60),
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

    # Imposta il timer massimo (es. 300 secondi = 5 minuti)
    max_game_time = 300
    
    tracker = HandTracker()  # Inizializza il tracciatore e la videocamera
    thread1 = threading.Thread(target=hand_tracking_thread, args=(cap, tracker, data_queue, stop_event))
    thread1.start()    

    game_thread = game_v2.GameThread(data_queue, stop_event, max_game_time, SETTINGS, PIECE_PATH)
    game_thread.run()
    
    thread1.join()
    
