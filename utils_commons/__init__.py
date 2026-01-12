import logging

logging.info("utils::utils_commons module is loaded.")

def clean_text(s: str) -> str:
    # Normalize whitespace and strip newlines etc.
    return " ".join(s.replace("\r", " ").replace("\n", " ").split()).strip()

