from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# Wczytaj model YOLOv8
model = YOLO("yolov8n.pt")

# Otwórz plik wideo
video_path = "/Users/dtomal/Documents/hackyeah-project-2k24/data_mp4/HY_2024_film_11.mp4"
cap = cv2.VideoCapture(video_path)

# Historia śledzenia
track_history = defaultdict(lambda: [])

# Pętla po klatkach wideo
while cap.isOpened():
    # Odczytaj klatkę z wideo
    success, frame = cap.read()

    if success:
        # Uruchom śledzenie YOLOv8 na klatce, zachowując ślady między klatkami
        results = model.track(frame, persist=True)

        if results is not None and len(results) > 0:
            # Sprawdź, czy wyniki są dostępne
            if results[0] is not None and hasattr(results[0], 'boxes'):
                boxes = results[0].boxes.xywh.cpu().numpy()
                print(results[0])
                track_ids = results[0].boxes.id.int().cpu().numpy().tolist()

                # Wizualizuj wyniki na klatce
                annotated_frame = results[0].plot()

                # Rysuj ślady
                for box, track_id in zip(boxes, track_ids):
                    x, y, w, h = box
                    track = track_history[track_id]
                    track.append((float(x), float(y)))  # Punkt środkowy x, y
                    if len(track) > 30:  # zachowaj 30 śladów
                        track.pop(0)

                    # Rysuj linie śledzenia
                    points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
                    cv2.polylines(annotated_frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)

                # Wyświetl zannotowaną klatkę
                cv2.imshow("YOLOv8 Tracking", annotated_frame)

        # Przerwij pętlę, jeśli naciśnięto 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        # Przerwij pętlę, jeśli osiągnięto koniec wideo
        break

# Zwolnij obiekt przechwytywania wideo i zamknij okno wyświetlania
cap.release()
cv2.destroyAllWindows()
