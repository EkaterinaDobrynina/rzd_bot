from db.models import User, Questionnaire
from db.database import Session, engine

import os
from dotenv import load_dotenv
import telebot
from keyboards import main_keyboard, delete_markup, show_markup, markup_choices, commands
from questions import QUESTIONS
from PIL import Image, ImageDraw, ImageFont
import pandas as pd


load_dotenv()
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
session = Session()


@bot.message_handler(['help', 'start'])
def greet(message):
    
    user = User(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
    )

    users = session.query(User).filter(User.telegram_id == user.telegram_id).all()
    if len(users) == 0:
        session.add(user)
        session.flush()
        session.commit()
        
        bot.send_message(message.chat.id, f"Привет! {user.first_name} \n Мы поможем создать карточку стажёра. Для старта нажми кнопку 'Cоздать карточку' или пропиши команду //start")
    else:
        user = session.query(User).filter_by(telegram_id=user.telegram_id).first()
        bot.send_message(
            message.chat.id,
            f"Привет! {user.first_name} \n Рады видеть тебя снова. Мы поможем создать карточку стажёра. Для старта нажми кнопку 'Cоздать карточку'\n{message.text}",
            reply_markup=main_keyboard()
        )
    bot.register_next_step_handler(message, lambda m: process_command(m, user))
    

@bot.message_handler()
def all_commands(message):
    
    user = User(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        
    )

    users = session.query(User).filter(User.telegram_id == user.telegram_id).all()
    if len(users) == 0:
        session.add(user)
        session.flush()
        session.commit()
    user = session.query(User).filter_by(telegram_id=user.telegram_id).first()
    process_command(message, user)


@bot.callback_query_handler(func=lambda call: call.data in ['yes_delete', 'no_delete', 'show_txt', 'show_jpg'])
def callback_query(call):
    if call.data == "yes_delete":
        user = session.query(User).filter_by(telegram_id=call.from_user.id).first()
        questions = session.query(Questionnaire).filter_by(user_id=user.id).all()
        for question in questions:
            session.delete(question)
        session.flush()
        session.commit()
        bot.answer_callback_query(call.id, "Предыдущие ответы удалены. Всего будет девять вопросов. Поехали!")
        process_questions(call.message, user, 'start_questionnaire')
    elif call.data == "no_delete":
        bot.answer_callback_query(call.id, "Хорошо")
        bot.send_message(call.message.chat.id, 'Спасибо за участие.', reply_markup=main_keyboard())
        bot.send_sticker(call.message.chat.id, 'CAACAgIAAxkBAAJljGVye9iYnc9z7hLEIlJB6O7AocolAAIoAAOhthEIflWOemMOfIszBA')
    elif call.data == "show_txt":
        user = session.query(User).filter_by(telegram_id=call.from_user.id).first()
        questions = session.query(Questionnaire).filter_by(user_id=user.id).all()
        answers = '\n'.join([f'{QUESTIONS[question.question_id]["text"].replace("?", '')}: {question.answer}' for question in questions])
        bot.send_message(call.message.chat.id, answers, reply_markup=main_keyboard())
    elif call.data == "show_jpg":
        bot.answer_callback_query(call.id, "Готовим визитку . . .")
        user = session.query(User).filter_by(telegram_id=call.from_user.id).first()
        ans = pd.read_sql_query(f'select answer from questionnaire where user_id = {user.id} and question_id NOT IN (1, 3, 7, 8)',con=engine)
        ans_n = ans.iloc[0]['answer']
        ans_t = ans.iloc[1:7]['answer']
        # ans_t = ans.iloc[1:7].to_string(index=False, header=False, col_space=30, justify='right')
        print(ans_t)
        jpg_file = create_jpg(ans_n, ans_t)
        bot.send_photo(call.message.chat.id, jpg_file, reply_markup=main_keyboard())

def create_jpg(name, body):
    step = 0
    image = Image.open('staz.jpg')
    font_n = ImageFont.truetype('DejaVuSans.ttf', 34)
    font_b = ImageFont.truetype('DejaVuSans.ttf', 28)
    drawer = ImageDraw.Draw(image)
    drawer.text((265, 30), name, font=font_n, fill='black')
    for elem in body.tolist():
        drawer.text((360, 165+step), str(elem), font=font_b, fill='black', spacing=15)
        print(elem)
        step+=47
    return image
def process_command(message, user):
    if message.text == commands['сreate']:
        if len(user.questionnaire) == 0:
            bot.send_message(message.chat.id, 'Поехали!')
            process_questions(message, user, 'start_questionnaire')
        elif len(user.questionnaire) == len(QUESTIONS):
            bot.send_message(message.chat.id, 'Ты уже заполнил анкету. Удали старые данные, чтобы заполнить заново?', reply_markup=delete_markup())
        else:
            bot.send_message(message.chat.id, 'На часть вопросов ты уже ответил, давай продолжим!')
            process_questions(message, user, 'start_questionnaire')
        
    elif message.text == commands['info']:
        bot.send_message(message.chat.id, "Этот бот поможет создать тебе небольшую анкету/визитку, чтобы ты мог быстрее познакомиться с куратором и своими коллегами!", reply_markup=main_keyboard())
    elif message.text == commands['delete']:
        questions = session.query(Questionnaire).filter_by(user_id=user.id).all()
        for question in questions:
            session.delete(question)
        session.flush()
        session.commit()
        bot.send_message(message.chat.id, "Предыдущие ответы удалены", reply_markup=main_keyboard())
    else:
        bot.reply_to(message, 'Что-то пошло не так, попробуй всё сначала. Или такую команду мы не знаем', reply_markup=main_keyboard())


def process_questions(message, user, status):
    if message.text in ['/start', '/help']:
        greet(message)
    else:
        session.flush()
        if status != 'start_questionnaire':
            assert status in list(range(len(QUESTIONS)))
            new_question = Questionnaire(
                user_id=user.id,
                question_id=status,
                answer=message.text,
            )
            session.add(new_question)
            session.flush()
            session.commit()
        status = len(user.questionnaire)
        if status < len(QUESTIONS):
            question = [question for question in QUESTIONS if question['id'] == status][0]
            msg = bot.send_message(message.chat.id, question['text'], reply_markup=markup_choices(question["choices"]))
            bot.register_next_step_handler(msg, lambda m: process_questions(m, user, status))
        else:
            bot.send_message(
                message.chat.id, 
                'Cпасибо. Ты ответил на все вопросы. Хочешь посмотреть результат? Ты можешь вывести его в форме анкеты или визитки.',
                reply_markup=show_markup())


bot.infinity_polling(restart_on_change=False)