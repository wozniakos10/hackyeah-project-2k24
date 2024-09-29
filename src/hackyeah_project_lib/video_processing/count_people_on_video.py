from typing import Any, Dict, Tuple

import cv2
from pydantic import BaseModel
from ultralytics import YOLO


class PeopleCountModel(BaseModel):
    number_of_persons: int
    description: str
    multiple_persons_in: float | None
    multiple_persons_out: float | None


def count_people(results: Any) -> int:
    count = 0
    for result in results:
        for obj in result.boxes.data:
            if int(obj[5]) == 0:  # Klasa 0 to 'person' w modelu COCO
                count += 1
    return count


def analyze_people_count(people_count_over_time: Any) -> Dict[str, Any]:
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


def analyze_video(
    video_path: str, model: Any = "yolov8n-pose.pt"
) -> Tuple[float | None, float | None, float | None, float | None]:
    model = YOLO(model)
    cap = cv2.VideoCapture(video_path)
    frame_number = 0
    people_count_over_time = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_number % 10 == 0:
            results = model.track(frame, stream=True)  # Użyj stream=True dla większej wydajności

            num_people = count_people(results)

            time_in_seconds = frame_number / fps

            people_count_over_time.append((time_in_seconds, num_people))

        # Zwiększ numer klatki
        frame_number += 1

    # Zwolnij zasoby
    cap.release()

    # Wyświetl tylko końcowe wyniki
    # print(people_count_over_time)

    analysis = analyze_people_count(people_count_over_time)
    person1_start = analysis["person_1_appears"]
    person2_start = analysis["person_2_appears"]
    person1_stop = analysis["person_1_disappears"]
    person2_stop = analysis["person_2_disappears"]
    return person1_start, person2_start, person1_stop, person2_stop


def num_people(
    person1_start: float | None, person2_start: float | None, person1_stop: float | None, person2_stop: float | None
) -> PeopleCountModel:
    if person1_start is None and person1_stop is None:
        if person1_start is None and person1_stop is None:
            return PeopleCountModel(
                number_of_persons=0,
                description="No people detected",
                multiple_persons_in=None,
                multiple_persons_out=None,
            )
    if person2_start is None and person2_stop is None:
        return PeopleCountModel(
            number_of_persons=1,
            description="A single person was detected on video",
            multiple_persons_in=None,
            multiple_persons_out=None,
        )
    return PeopleCountModel(
        number_of_persons=2,
        description=f"2 people from {person2_start} [s] to {person2_stop} [s]",
        multiple_persons_in=person2_start,
        multiple_persons_out=person2_stop,
    )


# Jak wolamy:
# Zwraca Tuple ('Opis liczby osob', liczba_osob)
# video_path = '/Users/dtomal/Documents/hackyeah-project-2k24/data_mp4/HY_2024_film_10.mp4'
# print(num_people(*analyze_video(video_path)))
