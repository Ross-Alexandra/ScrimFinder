import os
INTER_PROCESS_AUTH_KEY = os.getenv("SCRIM_FINDER_QUEUE_AUTH", "").encode()
if INTER_PROCESS_AUTH_KEY == b"":
    print("Warning: INTER_PROCESS_AUTH_KEY not set.")
INTER_PROCESS_PORT = int(os.getenv("SCRIM_FINDER_QUEUE_PORT", 0))
INTER_PROCESS_HOST = os.getenv("SCRIM_FINDER_QUEUE_HOST")

from scrim_finder.api.queue_objects.scrim import Scrim
