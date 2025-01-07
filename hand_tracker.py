import cv2
import mediapipe as mp
import numpy as np

class HandTracker:

    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarks_activated = True
        self.hand_landmarks = None

    def draw_landmarks(self, frame, hand_landmarks):
        mp.solutions.drawing_utils.draw_landmarks(
            frame,
            hand_landmarks,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2)
        )

    def is_pinching(self, threshold=0.05):
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
        
        if self.hand_landmarks is None:
            return False    

        landmarks = [(lm.x, lm.y, lm.z) for lm in self.hand_landmarks.landmark]
        finger_tip_list = [8,12,16,20]
        for finger_tip in finger_tip_list:
            if _finger_pinching(landmarks,4 , finger_tip):
                return True
        return False

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = self.hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.hand_landmarks = hand_landmarks        
                if self.landmarks_activated:
                    self.draw_landmarks(frame, hand_landmarks)                                    

        
        return frame, self.is_pinching()
        
        
def _get_board_layer(frame_width, frame_height, cell_size, grid_offset, color, thickness):    
    # Crea un layer vuoto per la griglia
    grid_layer = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    # Disegna la griglia una sola volta sul layer
    for row in range(8):  # Righe
        for col in range(8):  # Colonne
            pt1 = (grid_offset[0] + col * cell_size, grid_offset[1] + row * cell_size)
            pt2 = (pt1[0] + cell_size, pt1[1] + cell_size)
            cv2.rectangle(grid_layer, pt1, pt2, color, thickness)

    return grid_layer


def main():
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Errore nell'aprire la videocamera.")
        return
    board_layer = _get_board_layer(640,480,40,(80,80),(0,0,255),2)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Errore nel catturare il frame.")
            break

        frame = cv2.flip(frame, 1)
        frame_1 = cv2.addWeighted(frame, 1, board_layer, 1, 0)
        #frame = tracker.process_frame(frame)        
        cv2.imshow("Hand Tracking", frame_1)

        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):  # Esci
            break
        elif key == ord('h'):             
                help_activated = not help_activated
        elif key == ord('l'):
            landmarks_activated = not landmarks_activated

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
