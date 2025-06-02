import re

def detect_script(text: str) -> str:
    """
    Returns:
      - "hi" if any Devanagari characters (Hindi) are found
      - "ur" if any Arabic‐script characters (Urdu) are found
      - "en" otherwise (assumes Latin/English)
    """
    # Devanagari (Hindi) range: U+0900 to U+097F
    if re.search(r'[\u0900-\u097F]', text):
        return "hi"
    # Arabic‐script range (covers Urdu): U+0600 to U+06FF
    if re.search(r'[\u0600-\u06FF]', text):
        return "ur"
    # If neither Hindi nor Urdu markers, treat as English (Latin)
    return "en"