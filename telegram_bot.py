import os
import random
import telebot
import engine
import pymongo

user_mistake = ""
username = "kalashnikovstepan08"
password = "UJjMWWm4SgqYJQi0"
cluster_url = "cluster0.gdumxrw.mongodb.net"

# Construct the MongoDB Atlas connection string
mongo_url = f"mongodb+srv://{username}:{password}@{cluster_url}/test?retryWrites=true&w=majority"
#myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myclient = pymongo.MongoClient(mongo_url)
#myclient.drop_database('mydatabase')
mydb = myclient["mydatabase"]
mycol = mydb["user_data"]

BOT_TOKEN = os.environ.get('BOT_TOKEN')
print(BOT_TOKEN)
user_context = {}

bot = telebot.TeleBot(BOT_TOKEN)

questions = [
    "What is your first language?",
    "What is your second language?",
    "What is your current level?",
    "What is your desired level?"
]
questionsarr = []
answers = {}
completed_questionnaire = {}

mistake = ""


def initialize_mistake(user_id):
    global mistake
    if not mistake:
        # If 'mistake' is not assigned, generate it here
        mistakes = mycol.find({"user_id": user_id})[0]["mistakes"]
        if len(mistakes) > 0:
            mistake = random.choice(mistakes)


@bot.message_handler(commands=['start'], func=lambda message: not bool(mycol.count_documents({"user_id": message.chat.id}, limit = 1)))
def start(message):
    user_id = message.chat.id
    completed_questionnaire[user_id] = False
    answers[user_id] = {}
    send_question(user_id, 0)


def send_question(user_id, question_index):
    if question_index < len(questions):
        question = questions[question_index]
        bot.send_message(user_id, question)
        bot.register_next_step_handler_by_chat_id(user_id, process_answer, question_index)
    else:
        bot.send_message(user_id, "Thank you for completing the questionnaire! Wait for a bit for us to process your "
                                  "info")
        completed_questionnaire[user_id] = True
        user_answers = answers[user_id]
        processor = engine.ChatEngine(user_answers[questions[0]], user_answers[questions[1]],
                                      user_answers[questions[2]], user_answers[questions[3]])
        plan = processor.learning_plan_generation()
        smallTalkTopics = processor.small_talk_topics()
        mycol.insert_one({"user_id": user_id,
                          "lesson_count": 0,
                          "learning_plan": plan,
                          "small_talk_topics": smallTalkTopics,
                          "answers": list(user_answers.values()),
                          "mistakes": []},)
        documents = mycol.find()

        print(documents)
        bot.send_message(user_id, "Now you can start the lesson. Say \"Hello!\" to your tutor!")


def process_answer(message, question_index):
    user_id = message.chat.id
    answer = message.text
    question = questions[question_index]
    answers[user_id][question] = answer
    send_question(user_id, question_index + 1)


@bot.message_handler(func=lambda message: bool(mycol.count_documents({"user_id": message.chat.id}, limit = 1)))
def handle_message(message):

    user_id = message.chat.id
    cursor = mycol.find({"user_id": user_id})
    print(cursor)
    userInfo = cursor[0]
    print(userInfo)
    if user_id not in user_context:

        user_context[user_id] = {
            "conversation": [],
        }

    conversation = user_context[user_id]["conversation"]
    initialize_mistake(user_id)
    user_context[user_id]["conversation"].append({"role": "user", "content": message.text})
    chat = engine.ChatEngine(userInfo["answers"][0], userInfo["answers"][1], userInfo["answers"][2],
                             userInfo["answers"][3], userInfo["lesson_count"],
                             smallTalkTopics=userInfo["small_talk_topics"],
                             mistake=user_mistake, plan=userInfo["learning_plan"][userInfo["lesson_count"]])

    # Process the message and update conversation and state
    stop, response = chat.conversation(conversation)

    user_context[user_id]["conversation"].append({"role": "assistant", "content": response})
    # Send the response back to the user
    bot.send_message(user_id, response)

    if stop == 1:
        bot.send_message(user_id, "You've finished the lesson! Saving data...")
        myquery = {"user_id": user_id}
        mydoc = mycol.find(myquery)[0]
        mistakes = chat.mistakes_to_topics()
        mistakes.append(mydoc["mistakes"])
        chat.listOfAnswers = []
        newvalues = {"$set": {"lesson_count": mydoc["lesson_count"]+1}}
        mycol.update_one(myquery, newvalues)
        mistakes_update = {"$set": {"mistakes": mistakes}}
        mycol.update_one(myquery, mistakes_update)
        user_context[user_id]["conversation"] = []
        bot.send_message(user_id, "Now you can proceed with the next lesson.")



bot.polling()
