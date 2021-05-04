import os

db_host = os.getenv("POSTGRESHOST")
db = os.getenv("SIEGESCHEDULERDATABASE")
db_user = os.getenv("SIEGESCHEDULERUSER")
db_pass = os.getenv("SIEGESCHEDULERPASS")
db_port = os.getenv("POSTGRESPORT")