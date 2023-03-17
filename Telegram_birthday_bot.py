# -*- coding: utf-8 -*-
"""
Created on Fri Mar 17 09:34:46 2023

@author: Admin
"""

import csv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

# Define the states for the conversation handler
NAME, BIRTHDAY = range(2)

# Define the handler for the /start command
def start(update: Update, context):
    reply_keyboard = [['Yes', 'No']]
    update.message.reply_text(
        'Hi! My name is Birthday Bot. '
        'Do you want to tell me your name?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return NAME

# Define the handler for the user's name
def get_name(update: Update, context):
    name = update.message.text
    context.user_data['name'] = name
    update.message.reply_text(f'Hi {name}! When is your birthday? (DD/MM/YYYY)')
    return BIRTHDAY

# Define the handler for the user's birthday
def get_birthday(update: Update, context):
    birthday = update.message.text
    context.user_data['birthday'] = birthday

    # Save user data to a CSV file
    with open('user_data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([context.user_data['name'], context.user_data['birthday'], update.message.chat_id])

    update.message.reply_text(f'Thank you {context.user_data["name"]}! I will remember your information.')
    return ConversationHandler.END

# Define the function to send birthday greetings
def send_greetings(context):
    today = datetime.today().strftime('%d/%m')
    with open('user_data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1][0:5] == today:
                message = f'Happy birthday {row[0]}!'
                context.bot.send_message(chat_id=row[2], text=message)

# Define the main function to run the bot
def main():
    # Create the updater and dispatcher
    updater = Updater('YOUR_TOKEN_HERE', use_context=True)
    dispatcher = updater.dispatcher

    # Add the handlers to the dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            BIRTHDAY: [MessageHandler(Filters.regex(r'^\d{2}/\d{2}/\d{4}$'), get_birthday)]
        },
        fallbacks=[MessageHandler(Filters.regex(r'^Done$'), ConversationHandler.END)]
    )
    dispatcher.add_handler(conv_handler)

    # Start the updater and schedule the birthday greetings
    updater.start_polling()
    job_queue = updater.job_queue
    job_queue.run_daily(send_greetings, time=datetime.time(hour=9, minute=0, second=0))

    # Run the bot
    updater.idle()

if __name__ == '__main__':
    main()