from datetime import datetime
from multiprocessing.connection import Client
from flask import request
from flask_cors import cross_origin

from scrim_finder.api import app
from scrim_finder.api.codes import UserCodes, SystemCodes
from scrim_finder.api.queue_objects import Scrim, INTER_PROCESS_AUTH_KEY

# ============= HELPERS FOR THE ROUTES ================== #

def message_bot(queue_object):
    """ Sends [queue_object] to the consuming bot.
    
        Args:
            queue_obj (Scirm): The message to be sent to the bot.
     """

    rejected_counter = 0
    while True:
        try:
            connection = Client(('localhost', 34365), authkey=INTER_PROCESS_AUTH_KEY)
        except (ConnectionResetError, ConnectionRefusedError):
            if rejected_counter > 20:
                print("The service is down, and we cannot connect. Retried 20 times without success.")
                return SystemCodes.CommunicationError
            else:
                rejected_counter += 1
            continue

        except Exception as e:
            print(f"Exception trying to communicate with the bot: {e}")
            print(f"Exception of type {e.__class__}")
            return SystemCodes.CommunicationError
        break

    try:
        connection.send(queue_object)
        response_code = connection.recv()
    except Exception as e:
        print(f"Exception while trying to send or receive object. {e}")
        return SystemCodes.CommunicationError
    finally:
        connection.close()

    return response_code
        
# ======================== ROUTES ======================= #

@app.route("/scrim_request", methods=['POST'])
def scrim_request():
    data = request.get_json()
    required_parameters = ["team_name", "team_contact", "played_at", "maps"]

    if data is None or not all([x in data.keys() for x in required_parameters]):
        return "Missing Parameters on request", 400

    # Convert the data to usable formats.
    team_name = data["team_name"].lower()
    team_contact = data["team_contact"]
    played_at = datetime.utcfromtimestamp(data["played_at"] / 1000)
    maps = [requested_map.lower() for requested_map in data["maps"]]

    new_scrim = Scrim(team_name, team_contact, played_at, maps)
    scrim_response = message_bot(new_scrim)

    if scrim_response is not SystemCodes.Good:
        print(f"Failed to create scrim. Error code {scrim_response.value}")
        return f"Failed to book scrim. Error code {scrim_response.value}", 400

    return "OK", 200
