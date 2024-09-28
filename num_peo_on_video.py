import cv2
from ultralytics import YOLO


# Funkcja do zliczania osób na klatce
def count_people(results):
    count = 0
    for result in results:
        # YOLO zwraca detekcje w formie listy obiektów, sprawdzamy klasę (person = 0)
        for obj in result.boxes.data:
            if int(obj[5]) == 0:  # Klasa 0 to 'person' w modelu COCO
                count += 1
    return count


def analyze_people_count(people_count_over_time):
    person_1_appears = None
    person_2_appears = None
    person_2_disappears = None
    person_1_disappears = None

    for i, (time, count) in enumerate(people_count_over_time):
        if count >= 1 and person_1_appears is None:
            person_1_appears = time  # Pierwsza osoba pojawia się
        if count >= 2 and person_2_appears is None:
            person_2_appears = time  # Druga osoba pojawia się
        if count < 2 and person_2_appears is not None and person_2_disappears is None:
            person_2_disappears = time  # Druga osoba znika
        if count < 1 and person_1_appears is not None and person_1_disappears is None:
            person_1_disappears = time  # Pierwsza osoba znika

    return {
        "person_1_appears": person_1_appears,
        "person_2_appears": person_2_appears,
        "person_2_disappears": person_2_disappears,
        "person_1_disappears": person_1_disappears,
    }

# Ścieżka do wideo
video_path = '/Users/dtomal/Documents/hackyeah-project-2k24/data_mp4/HY_2024_film_11.mp4'

# Wczytanie modelu YOLO
model = YOLO('yolov8n-pose.pt')

# Otwórz plik wideo za pomocą OpenCV
cap = cv2.VideoCapture(video_path)

# Zmienna do przechowywania numeru klatki
frame_number = 0

# Zmienna do przechowywania liczby osób w czasie (sekundy, liczba osób)
people_count_over_time = []

# Zmienna do śledzenia klatek na sekundę (fps)
fps = cap.get(cv2.CAP_PROP_FPS)

# Pętla do przetwarzania wideo
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Analizuj co 10 klatkę (aby było jeszcze szybciej)
    if frame_number % 10 == 0:
        # YOLO analizuje klatkę
        results = model.track(frame, stream=True)  # Użyj stream=True dla większej wydajności

        # Zlicz liczbę osób w klatce
        num_people = count_people(results)

        # Oblicz czas wideo (frame_number / fps)
        time_in_seconds = frame_number / fps

        # Dodaj wyniki (czas, liczba osób)
        people_count_over_time.append((time_in_seconds, num_people))

    # Zwiększ numer klatki
    frame_number += 1

# Zwolnij zasoby
cap.release()

# Wyświetl tylko końcowe wyniki
print(people_count_over_time)

analysis = analyze_people_count(people_count_over_time)

# Wyświetl wyniki analizy
print(f"Pierwsza osoba pojawia się w sekundzie: {analysis['person_1_appears']:.2f}" if analysis['person_1_appears'] else "Brak detekcji pierwszej osoby.")
print(f"Druga osoba pojawia się w sekundzie: {analysis['person_2_appears']:.2f}" if analysis['person_2_appears'] else "Brak detekcji drugiej osoby.")
print(f"Druga osoba znika w sekundzie: {analysis['person_2_disappears']:.2f}" if analysis['person_2_disappears'] else "Druga osoba nie zniknęła.")
print(f"Pierwsza osoba znika w sekundzie: {analysis['person_1_disappears']:.2f}" if analysis['person_1_disappears'] else "Pierwsza osoba nie zniknęła.")




