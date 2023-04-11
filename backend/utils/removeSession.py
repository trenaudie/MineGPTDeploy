import os
import time

SESSION_DIR = 'backend/session_files'
MAX_AGE_DAYS = 0.01 #around 900 seconds

FRONT_SESSION_DIR = "session_files"

now = time.time()
if __name__ == "__main__":
    print(f"Removing files older than {MAX_AGE_DAYS*24*3600} seconds from {SESSION_DIR}...")
    for filename in os.listdir(SESSION_DIR):
        filepath = os.path.join(SESSION_DIR, filename)
        if os.path.isfile(filepath) and (now - os.path.getmtime(filepath)) > MAX_AGE_DAYS * 24 * 3600:
            os.remove(filepath)

    print(f"Removing files older than {MAX_AGE_DAYS*24*3600} seconds from {FRONT_SESSION_DIR}...")
    for filename in os.listdir(FRONT_SESSION_DIR):
        filepath = os.path.join(FRONT_SESSION_DIR, filename)
        if os.path.isfile(filepath) and (now - os.path.getmtime(filepath)) > MAX_AGE_DAYS * 24 * 3600:
            os.remove(filepath)
