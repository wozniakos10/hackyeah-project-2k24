import joblib
import pandas as pd


class xgboostclass:
    def __init__(self, model_path: str, scaler_path: str) -> None:
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
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
