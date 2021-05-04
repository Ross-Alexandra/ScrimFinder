import os
INTER_PROCESS_AUTH_KEY = os.getenv("INTERPROCESSAUTHKEY", "").encode()
if INTER_PROCESS_AUTH_KEY == b"":
    print("Warning: INTER_PROCESS_AUTH_KEY not set.")

from scrim_finder.api.queue_objects.scrim import Scrim