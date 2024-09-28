import logging
import os


def get_configured_logger(name: str, log_file: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """
    Tworzy i zwraca skonfigurowany logger.

    :param name: Nazwa loggera.
    :param log_file: Opcjonalna ścieżka do pliku logu. Jeśli None, logi będą wyświetlane w konsoli.
    :param level: Poziom logowania (np. logging.DEBUG, logging.INFO).
    :return: Skonfigurowany logger.
    """
    # Tworzenie loggera z podaną nazwą
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Sprawdzenie, czy logger już nie ma zdefiniowanych handlerów
    if not logger.hasHandlers():
        # Ustawienia formatu logów
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Tworzenie handlera dla konsoli
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Jeżeli podano ścieżkę do pliku, dodaj handler pliku
        if log_file:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)  # Tworzenie folderów, jeśli nie istnieją
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


# Przykład użycia:
if __name__ == "__main__":
    logger = get_configured_logger("my_logger", log_file="logs/application.log", level=logging.DEBUG)

    logger.debug("To jest debug.")
    logger.info("To jest informacja.")
    logger.warning("To jest ostrzeżenie.")
    logger.error("To jest błąd.")
    logger.critical("To jest krytyczny błąd.")
