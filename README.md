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
