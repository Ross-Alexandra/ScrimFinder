from datetime import datetime


class Scrim:
    
    def __init__(self, team_name: str, scrim_type: str, team_contact: str, played_at: datetime, map_names: list):
        self.team_name = team_name
        self.scrim_type = scrim_type
        self.played_at = played_at
        self.team_contact = team_contact
        self.map_names = map_names
        self.contact_type = "Discord"
    
    def __str__(self):
        return f"Team {self.team_name} is LFS {self.scrim_type} played_at {self.played_at} on {self.map_names}. Contact {self.team_contact}"
