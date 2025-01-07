import cv2
import mediapipe as mp
import os
import time
import json
import math
import numpy as np

def is_pinching(landmarks, threshold=0.05):
    """
    Determina se viene eseguito il gesto di pinching (pollice e indice vicini).

    :param landmarks: Lista di tuple (x, y, z) dei landmarks della mano.
    :param thumb_tip_index: Indice del landmark della punta del pollice.
    :param index_tip_index: Indice del landmark della punta dell'indice.
    :param threshold: Soglia massima di distanza per considerare il gesto come pinching.
    :return: True se il gesto di pinching è rilevato, False altrimenti.
    """
    def _finger_pinching(landmarks, thumb_tip_index=4, index_tip_index=8, threshold=0.05):
        # Ottieni i punti chiave
        thumb_tip = np.array([landmarks[thumb_tip_index][0], landmarks[thumb_tip_index][1]])
        index_tip = np.array([landmarks[index_tip_index][0], landmarks[index_tip_index][1]])

        # Calcola la distanza euclidea tra la punta del pollice e la punta dell'indice
        distance = np.linalg.norm(thumb_tip - index_tip)

        # Ritorna True se la distanza è sotto la soglia
        return distance < threshold
    finger_tip_list = [8,12,16,20]
    for finger_tip in finger_tip_list:
        if _finger_pinching(landmarks,4 , finger_tip):
            return True
    return False

def check_fingers(cv2,landmarks):

    def is_finger_extended_v3(landmarks, finger_indices, palm_index, tolerance=0.05):
        """
        Determina se un dito è disteso o piegato in base alla posizione dei landmark relativi alla mano.

        :param landmarks: Lista di tuple (x, y, z) dei landmarks della mano.
        :param finger_indices: Lista di indici che rappresentano i punti del dito (base alla punta).
        :param palm_index: Indice del metacarpo della mano (usato come riferimento per la direzione del dito).
        :param tolerance: Tolleranza massima per considerare i punti allineati.
        :return: True se il dito è disteso, False altrimenti.
        """
        # Ottieni i punti chiave
        palm_point = np.array([landmarks[palm_index][0], landmarks[palm_index][1]])  # Metacarpo della mano
        base_point = np.array([landmarks[finger_indices[0]][0], landmarks[finger_indices[0]][1]])  # Base del dito
        tip_point = np.array([landmarks[finger_indices[-1]][0], landmarks[finger_indices[-1]][1]])  # Punta del dito

        # Calcola il vettore della retta che collega palm_point -> tip_point
        palm_to_tip_vector = tip_point - palm_point

        # Calcola la distanza dei punti intermedi dalla retta palm_point -> tip_point
        distances_from_line = []
        for i in finger_indices[1:-1]:  # Considera solo i punti intermedi (esclude base e punta)
            point = np.array([landmarks[i][0], landmarks[i][1]])
            # Proietta il punto sulla retta e calcola la distanza
            palm_to_point_vector = point - palm_point
            projection_length = np.dot(palm_to_point_vector, palm_to_tip_vector) / np.linalg.norm(palm_to_tip_vector)**2
            projected_point = palm_point + projection_length * palm_to_tip_vector
            distance = np.linalg.norm(projected_point - point)
            distances_from_line.append(distance)

        # Verifica che tutte le distanze siano entro la tolleranza
        if not all(d <= tolerance for d in distances_from_line):
            return False

        # Verifica la progressività dei punti
        cumulative_distances = []
        for i in finger_indices:
            point = np.array([landmarks[i][0], landmarks[i][1]])
            distance_from_base = np.linalg.norm(point - base_point)
            cumulative_distances.append(distance_from_base)

        # Controlla che ogni punto sia progressivamente più distante dal precedente
        for i in range(1, len(cumulative_distances)):
            if cumulative_distances[i] <= cumulative_distances[i - 1]:
                return False

        return True
    def is_finger_extended_v2(landmarks, finger_indices, palm_index, tolerance=0.05):
        """
        Determina se un dito è disteso o piegato in base alla posizione dei landmark relativi alla mano.

        :param landmarks: Lista di tuple (x, y, z) dei landmarks della mano.
        :param finger_indices: Lista di indici che rappresentano i punti del dito (base alla punta).
        :param palm_index: Indice del metacarpo della mano (usato come riferimento per la direzione del dito).
        :param tolerance: Tolleranza massima per considerare i punti allineati.
        :return: True se il dito è disteso, False altrimenti.
        """
        # Ottieni i punti chiave
        palm_point = np.array([landmarks[palm_index][0], landmarks[palm_index][1]])  # Metacarpo della mano
        base_point = np.array([landmarks[finger_indices[0]][0], landmarks[finger_indices[0]][1]])  # Base del dito
        tip_point = np.array([landmarks[finger_indices[-1]][0], landmarks[finger_indices[-1]][1]])  # Punta del dito

        # Calcola il vettore della retta che collega palm_point -> tip_point
        palm_to_tip_vector = tip_point - palm_point

        # Calcola la distanza dei punti intermedi dalla retta palm_point -> tip_point
        distances_from_line = []
        for i in finger_indices[1:-1]:  # Considera solo i punti intermedi (esclude base e punta)
            point = np.array([landmarks[i][0], landmarks[i][1]])
            # Proietta il punto sulla retta e calcola la distanza
            palm_to_point_vector = point - palm_point
            projection_length = np.dot(palm_to_point_vector, palm_to_tip_vector) / np.linalg.norm(palm_to_tip_vector)**2
            projected_point = palm_point + projection_length * palm_to_tip_vector
            distance = np.linalg.norm(projected_point - point)
            distances_from_line.append(distance)

        # Verifica che tutte le distanze siano entro la tolleranza
        return all(d <= tolerance for d in distances_from_line)
    def is_finger_extended(landmarks, finger_indices, tolerance=0.03):
        """
        Determina se un dito è disteso o piegato in base ai landmarks.

        :param landmarks: Lista di tuple (x, y, z) dei landmarks della mano.
        :param finger_indices: Lista di indici che rappresentano i punti del dito (dalla base alla punta).
        :param tolerance: Tolleranza massima per considerare i punti allineati.
        :return: True se il dito è disteso, False altrimenti.
        """
        # Ottieni i punti del dito
        finger_points = [landmarks[i] for i in finger_indices]

        # Estrai solo le coordinate x e y (ignora z per semplicità)
        finger_points_2d = np.array([[p[0], p[1]] for p in finger_points])

        # Calcola il vettore che collega la base alla punta del dito
        base_to_tip_vector = finger_points_2d[-1] - finger_points_2d[0]
        
        # Calcola la distanza del punto iniziale (base) dai punti intermedi
        distances_from_line = []
        for point in finger_points_2d[1:-1]:  # Saltiamo base e punta
            # Proietta il punto sulla retta che va dalla base alla punta
            base_to_point_vector = point - finger_points_2d[0]
            projection_length = np.dot(base_to_point_vector, base_to_tip_vector) / np.linalg.norm(base_to_tip_vector)**2
            projected_point = finger_points_2d[0] + projection_length * base_to_tip_vector

            # Calcola la distanza tra il punto reale e quello proiettato
            distance = np.linalg.norm(projected_point - point)
            distances_from_line.append(distance)

        # Se tutte le distanze sono sotto la tolleranza, il dito è disteso
        return all(d <= tolerance for d in distances_from_line)

    # Indici dei landmark per ciascun dito (in ordine: pollice, indice, medio, anulare, mignolo)
    finger_indices_list = {
        "Pollice": [1, 2, 3, 4],
        "Indice": [5, 6, 7, 8],
        "Medio": [9, 10, 11, 12],
        "Anulare": [13, 14, 15, 16],
        "Mignolo": [17, 18, 19, 20]
    }
    
    # Inizializza contatore per dita distese
    extended_fingers = ""

    # Ciclo per ciascun dito
    for finger_name, finger_indices in finger_indices_list.items():
        # Verifica se il dito è disteso
        is_extended = is_finger_extended_v3(landmarks, finger_indices, 0, tolerance=0.03)
        
        # Incrementa il contatore se il dito è disteso
        if is_extended:
            extended_fingers += (finger_name + " ")

    # Stampa la lista di dita distese
    # print(f"Dita distese: {extended_fingers}")

def _main():
    
    def rileva_cap(hands,cap):
        # Apri la videocamera        
        i = 3
        landmarks_activated = True
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
                    
                    if landmarks_activated:
                        # Disegna i landmark e le connessioni sul frame originale
                        mp.solutions.drawing_utils.draw_landmarks(
                            frame,
                            hand_landmarks,
                            mp.solutions.hands.HAND_CONNECTIONS,
                            mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),  # Landmark
                            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2)  # Connessioni
                        )
                                    
                    # Qui x e y sono la posizione del primo landmark (indice), moltiplicato per le dimensioni della finestra
                    x = int(hand_landmarks.landmark[8].x * frame.shape[1])  
                    y = int(hand_landmarks.landmark[8].y * frame.shape[0])  

                    # Disegna il puntatore
                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

                    #mostra_distanza(results)
                    # Ottieni i landmarks come lista di tuple (x, y, z)
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

                    # Verifica il gesto di pinching
                    if is_pinching(landmarks):                        
                        cv2.putText(frame, "Pinching!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    else :
                        check_fingers(cv2,landmarks)

                    
                    
                    

            # Mostra il frame con i landmark disegnati
            cv2.imshow('Hand Landmarks', frame)

            # Controlla se è stato premuto un tasto
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Esci dal loop se premi 'q'
                break
            elif key == ord('a'): # Analizza
                print(analizza_mano(hand_landmarks))
            elif key == ord('s'):  # Salva l'immagine se premi 's'
                # Percorso della cartella di salvataggio
                save_folder = "imgs/"  # Modifica con il percorso della tua cartella
                # Percorso del file markdown per i log
                log_file_path = "Rilevamenti-mani.md"
                # Crea la cartella se non esiste
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)

                with open(log_file_path, "a") as log_file:  # 'a' per aggiungere ai log esistenti
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

                    if i == 3: log_file.write("## Test n \n Questi rilevamenti sono stati effettuati con la mano aperta frontalmente alla camera, a diverse distanze, con il monitor perpendicolare al terreno e la mano tendenzialmente parallela al monitor. \n### Rilevamenti di hand-landmarks a diverse distanze \n")                

                    log_file.write(f"-\t  **~ {i}0 cm**\n")
                    log_file.write(f"\t ![Hand landmark]({image_path}) \n")
                    log_file.write("\n| Dito | Pollice | Indice | Medio | Anulare | Mignolo | \n| ---------------- | ------- | ------ | ----- | ------- | ------- | \n| Distanza mcp-tip | ")
                    for finger, (mcp, tip) in finger_points.items():
                        dist = distance_3d(mcp, tip)
                        log_file.write(f"{dist:.3f} |")                
                    log_file.write("\n \n --- \n")                
                    i+=1
            elif key == ord('l'):
                landmarks_activated = not landmarks_activated
    cap = cv2.VideoCapture(0)
    try:        
        # Inizializza il rilevatore di mani
        hands = mp.solutions.hands.Hands(
            static_image_mode=False,       # Per rilevamento continuo (False per rilevamento in video)
            max_num_hands=1,               # Rileva una sola mano (impostabile a 2 se serve)
            min_detection_confidence=0.5,  # Confidenza minima per rilevare la mano
            min_tracking_confidence=0.5    # Confidenza minima per il tracciamento
        ) 
        rileva_cap(hands,cap)            

    except Exception as e:
        print(f"Errore: {e}")
    finally:
        hands.close()

    # Rilascia la videocamera e chiudi le finestre
    cap.release()
    cv2.destroyAllWindows()

_main()