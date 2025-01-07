import pygame
import time
import threading

class CountdownTimer:
    def __init__(self, total_seconds):
        """
        Inizializza il timer con il tempo totale in secondi.
        """
        self.total_seconds = total_seconds
        self.running = False
        self.window_size = (300, 150)
        self.font_size = 74

    def start(self):
        """
        Avvia il conto alla rovescia e mostra la finestra.
        """
        self.running = True
        threading.Thread(target=self._run_timer).start()

    def _run_timer(self):
        """
        Logica interna per il conto alla rovescia.
        """
        pygame.init()
        window = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Countdown Timer")
        font = pygame.font.Font(None, self.font_size)
        clock = pygame.time.Clock()

        start_time = time.time()
        remaining_time = self.total_seconds

        while self.running and remaining_time > 0:
            # Calcola il tempo rimanente
            elapsed = int(time.time() - start_time)
            remaining_time = max(self.total_seconds - elapsed, 0)

            # Calcola minuti e secondi
            minutes = remaining_time // 60
            seconds = remaining_time % 60

            # Gestisce eventi della finestra
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

            # Disegna il timer nella finestra
            window.fill((0, 0, 0))
            timer_text = font.render(f"{minutes:02}:{seconds:02}", True, (255, 255, 255))
            window.blit(timer_text, (self.window_size[0] // 2 - timer_text.get_width() // 2,
                                     self.window_size[1] // 2 - timer_text.get_height() // 2))
            pygame.display.flip()
            clock.tick(30)

        # Timer scaduto, chiude la finestra
        pygame.quit()

    def stop(self):
        """
        Ferma il conto alla rovescia e chiude la finestra.
        """
        self.running = False
