# Scrim Finder
Scrim finder is broken down into 2 different bots acting with a frontend UI and Database binding the two.

# NASC Bot
This is the bot which gives scrim_finder it's name. The NASC bot is responsible for proposing scrims
to teams based off timing provided in the frontend UI

# Schedule Bot
A bot for helping a team manage their schedule. A team will post an availability (which will be injected
into the NASC database). The NASC database will attempt to match a scrim, to the team's required availability.
If a match can't be found, then a custom URL on the scrim finder will be created. This link can be posted by the
team in their LFS post allowing others to fill in a scrim proposal.

# Development

## React App
The react app requires no additional setup to run in the dockerized environment.

## Flask App
In order to run the Flask App in the dockerized environment, the following environmental variables must be present:
 - NASCBOT_TOKEN (NASC_BOT's token.)
 - SCRIMFINDERDB (The db to connect to on the postgres server.)
 - POSTGRESHOST (The host for the postgres server.)
 - POSTGRESPORT (The host port for the postgres server.)
 - SCRIMFINDERUSER (The user for the db on the postgres server.)
 - SCRIMFINDERPASS (The password for the user on the db for the postgres server.)
 - ENVIRONMENT (Either "DEVELOPMENT" or "PRODUCTION". Used to decide acceptable origins for CORS)

\* Please note, in the present version of the bot, the AUTH token used for the inter-process communication queue
is set to be NASC Bot's token. This is because the queue is inaccessable via firewall rules and thus
the token doesn't need to be unique. A threat does exist here however, and the token should be unique at some point.

 ## NASC Bot
 In order to run the NASC Bot in the dockerized environment, the following environmental variables must be present:
 - NASCBOT_TOKEN (NASC_BOT's token.)
 - SCRIMFINDERDB (The db to connect to on the postgres server.)
 - POSTGRESHOST (The host for the postgres server.)
 - POSTGRESPORT (The host port for the postgres server.)
 - SCRIMFINDERUSER (The user for the db on the postgres server.)
 - SCRIMFINDERPASS (The password for the user on the db for the postgres server.)

