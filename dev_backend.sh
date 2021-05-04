py -m scrim_finder.schedule_bot.bot
py -m scrim_finder.nasc_bot.bot

export FLASK_ENV=development
export FLASK_APP=scrim_finder:app
flask run