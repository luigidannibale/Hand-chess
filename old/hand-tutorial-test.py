import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarks_activated = True

    def draw_landmarks(self, frame, hand_landmarks):
        mp.solutions.drawing_utils.draw_landmarks(
            frame,
            hand_landmarks,
            mp.solutions.hands.HAND_CONNECTIONS,
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
            mp.solutions.drawing_utils.DrawingSpec(color=(0, 0, 255), thickness=2)
        )

    def is_pinching(self, landmarks, threshold=0.05):
        thumb_tip = np.array([landmarks[4][0], landmarks[4][1]])
        index_tip = np.array([landmarks[8][0], landmarks[8][1]])
        distance = np.linalg.norm(thumb_tip - index_tip)
        return distance < threshold

    def process_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if self.landmarks_activated:
                    self.draw_landmarks(frame, hand_landmarks)
                landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                if self.is_pinching(landmarks):
                    cv2.putText(frame, "Pinching!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        return frame

def main():
    tracker = HandTracker()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Errore nell'aprire la videocamera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Errore nel catturare il frame.")
            break

        frame = cv2.flip(frame, 1)
        frame = tracker.process_frame(frame)
        cv2.imshow("Hand Tracking", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Esci
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
