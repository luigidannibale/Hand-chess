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

def _main():
    def draw_hand_landmarks(frame,hand_landmarks):
        # Disegna i landmark e le connessioni sul frame originale
        mp.solutions.drawing_utils.draw_landmarks(
            frame,
            hand_landmarks,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),  # Landmark
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2)  # Connessioni
        )

    def traspone_cursor(frame,hand_landmarks):
        # Qui x e y sono la posizione del primo landmark (indice), moltiplicato per le dimensioni della finestra
        x = int(hand_landmarks.landmark[8].x * frame.shape[1])  
        y = int(hand_landmarks.landmark[8].y * frame.shape[0])  
        # Disegna il puntatore
        cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

    def rileva_cap(hands,cap):
        # Apri la videocamera        
        
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
                        draw_hand_landmarks(frame,hand_landmarks);
                        
                    traspone_cursor(frame,hand_landmarks)                         
                    
                    # Ottieni i landmarks come lista di tuple (x, y, z)
                    landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]

                    # Verifica il gesto di pinching
                    if is_pinching(landmarks):                        
                        cv2.putText(frame, "Pinching!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
                    

                    
            # Mostra il frame con i landmark disegnati            
            cv2.imshow('Hand Landmarks', frame)

            # Controlla se è stato premuto un tasto
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):  # Esci dal loop se premi 'q'
                break
            elif key == ord('p'): 
                print("Hai premuto p")
            elif key == ord('h'): 
                help_activated = not help_activated
            elif key == ord('l'):
                landmarks_activated = not landmarks_activated
    
    cap = cv2.VideoCapture(0)
    try:        
        # Inizializza il rilevatore di mani
        hands = mp.solutions.hands.Hands(
            static_image_mode=False,       # Per rilevamento continuo (False per rilevamento in video)
            max_num_hands=2,               # Rileva una sola mano (impostabile a 2 se serve)
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