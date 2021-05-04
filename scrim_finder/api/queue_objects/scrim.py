class Scrim:
    
    def __init__(self, team_name, team_contact, played_at, map_names):
        self.team_name = team_name
        self.played_at = played_at
        self.team_contact = team_contact
        self.map_names = map_names
        self.contact_type = "Discord"
    
    def __str__(self):
        return f"team: {self.team_name}, played_at: {self.played_at} on maps: {self.map_names}. Contact {self.team_contact}"
