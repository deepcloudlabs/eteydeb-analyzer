import logging

logging.info("utils::utils_http module is loaded.")

def read_cookies() -> str:
    cookies = ""
    with open("cookies.txt", "r", encoding="utf-8") as cookie_file:
        for line in cookie_file:
            cookies += line.strip()
    return cookies