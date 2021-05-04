start py -m scrim_finder.schedule_bot.bot
start py -m scrim_finder.nasc_bot.bot

set FLASK_APP=scrim_finder:app
set FLASK_ENV=development
flask run