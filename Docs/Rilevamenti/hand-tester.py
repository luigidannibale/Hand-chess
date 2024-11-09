import cv2
import mediapipe as mp
import os
import math
import time

# Funzione per calcolare la distanza 3D
def distance_3d(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 +
                    (point1.y - point2.y) ** 2 +
                    (point1.z - point2.z) ** 2)

# Percorso della cartella di salvataggio
save_folder = "imgs/"  # Modifica con il percorso della tua cartella
# Percorso del file markdown per i log
log_file_path = "Rilevamenti-mani.md"
# Crea la cartella se non esiste
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

# Inizializza MediaPipe Hands e MediaPipe Drawing
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Apri la videocamera
cap = cv2.VideoCapture(0)

# Inizializza il rilevatore di mani
with mp_hands.Hands(
    static_image_mode=False,       # Per rilevamento continuo (False per rilevamento in video)
    max_num_hands=1,               # Rileva una sola mano (impostabile a 2 se serve)
    min_detection_confidence=0.5,  # Confidenza minima per rilevare la mano
    min_tracking_confidence=0.5    # Confidenza minima per il tracciamento
) as hands:
    with open(log_file_path, "a") as log_file:  # 'a' per aggiungere ai log esistenti
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Errore nel catturare il frame.")
                break

            # Specchia l'immagine sull'asse orizzontale
            frame = cv2.flip(frame, 1)

            # Converte il frame in RGB (MediaPipe richiede RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Rileva i landmark della mano
            results = hands.process(frame_rgb)

            # Se vengono rilevati landmark, disegnarli sul frame
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Disegna i landmark e le connessioni sul frame originale
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),  # Landmark
                        mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)  # Connessioni
                    )

            # Mostra il frame con i landmark disegnati
            cv2.imshow('Hand Landmarks', frame)

            # Controlla se è stato premuto un tasto
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Esci dal loop se premi 'q'
                break
            elif key == ord('s'):  # Salva l'immagine se premi 's'
                
                timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                # Costruisci il percorso del file di salvataggio
                image_path = os.path.join(save_folder, f"hand_landmark_{timestamp}.png")
                cv2.imwrite(image_path, frame)
                # Dizionario con i punti MCP e Tip per ogni dito
                finger_points = {
                    "Pollice": (hand_landmarks.landmark[2], hand_landmarks.landmark[4]),  # MCP Pollice e Tip Pollice
                    "Indice": (hand_landmarks.landmark[5], hand_landmarks.landmark[8]),   # MCP Indice e Tip Indice
                    "Medio": (hand_landmarks.landmark[9], hand_landmarks.landmark[12]),   # MCP Medio e Tip Medio
                    "Anulare": (hand_landmarks.landmark[13], hand_landmarks.landmark[16]), # MCP Anulare e Tip Anulare
                    "Mignolo": (hand_landmarks.landmark[17], hand_landmarks.landmark[20])  # MCP Mignolo e Tip Mignolo
                }
                print(f"Immagine salvata come {image_path} \n\n")
                log_file.write("## Distanza ~ \n")
                log_file.write(f"![[{image_path}]] \n")
                # Calcolo e stampa della distanza per ogni dito
                log_file.write("Distanza mcp-tip: \n")
                for finger, (mcp, tip) in finger_points.items():
                    dist = distance_3d(mcp, tip)
                    log_file.write(f"{finger} - {dist:.3f} \n")                
                log_file.write("\n --- \n")                



# Rilascia la videocamera e chiudi le finestre
cap.release()
cv2.destroyAllWindows()
