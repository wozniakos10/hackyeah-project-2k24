import os
from pathlib import Path

import joblib
import pandas as pd
from pydantic import BaseModel

CURRENT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class XGBoostPauseClassifierModel(BaseModel):
    raw_score: int
    interpretation: str


class XGBoostClassifier:
    def __init__(self) -> None:
        self.model_path = CURRENT_DIR.joinpath("xgboost_model.pkl")
        self.scaler_path = CURRENT_DIR.joinpath("scaler.pkl")
        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.mapper = {0: "pauza/przerywnik", 1: "nic"}

    def predict(self, data: dict[str, list[int]]) -> int:
        # dict example
        # new_data = {
        #     "pause_sum": [4000],
        #     "pause_percent": [0.4],
        #     "amount_of_pauses": [3]
        # }

        # Przygotowanie nowych danych do predykcji (przykład)

        new_df = pd.DataFrame(data)

        # Normalizacja danych (używając wcześniej wytrenowanego scalera)
        new_data_scaled = self.scaler.transform(new_df)

        # Wykonaj predykcję
        predictions = self.model.predict(new_data_scaled)

        # Wyświetl wyniki
        print("Predykcje:", predictions)

        return int(predictions[0])

    @staticmethod
    def format_output(score: int) -> XGBoostPauseClassifierModel:
        if score == 0:
            return XGBoostPauseClassifierModel(
                raw_score=score, interpretation="W danym nagraniu występują za długie pauzy lub przerywniki."
            )
        else:
            return XGBoostPauseClassifierModel(
                raw_score=score, interpretation="W danym nagraniu nie wykryliśmy zbyt długich pauz lub przerywników."
            )
