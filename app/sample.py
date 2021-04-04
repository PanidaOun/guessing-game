from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
import json
import redis

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                          '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get(
    "REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

@application.route('/')
def index():
    body = '<h2 style="color:white;background-color:darkblue; font-size:50px;">Alphabet Guessing Game V.1.0</h2>'
    db_game = db.game
    game = db.game.find_one()
    if game == None:
        mydict = {
            "question": ["_", "_", "_", "_"],
            "guessing": ["*", "*", "*", "*"],
            "answer": [],
            "fail": 0,
            "step": 0
        }
        db_game.insert_one(mydict)
    question = ' '.join(game['question'])
    body += ' <h3 style="font-size:30px;">Please Choose A or B or C or D to add the character to the question.</h3>'
    body += '<h3 style="font-size:20px;">Question: </h3>' + question
    body += '<h3 style="font-size:20px;">Choose: <button > <a href="/choiceA">A</a></button> <button> <a href="/choiceB">B</a></button> <button> <a href="/choiceC">C</a></button> <button> <a href="/choiceD">D</a></button></h3>'
    if game['step'] == 4:
        db_game.update_one({}, {"$set": {"step": 0}})
        return gamepage()
    return body


@application.route('/choiceA')
def choiceA():
    return choice1('A')

@application.route('/choiceB')
def choiceB():
    return choice1('B')

@application.route('/choiceC')
def choiceC():
    return choice1('C')

@application.route('/choiceD')
def choiceD():
    return choice1('D')

@application.route('/choiceA2')
def choiceA2():
    return choice2('A')
    
@application.route('/choiceB2')
def choiceB2():
    return choice2('B')

@application.route('/choiceC2')
def choiceC2():
    return choice2('C')

@application.route('/choiceD2')
def choiceD2():
    return choice2('D')

def choice1(chars):
    db_game = db.game
    game = db_game.find_one()
    curr = game["step"]
    db_game.update_one({}, {"$set": {"question." + str(curr): str(chars)}})
    db_game.update_one({}, {"$set": {"step": curr+1}})
    return index()

def choice2(chars):
    db_game = db.game
    game = db_game.find_one()
    curr = game["step"]
    fail = game["fail"]
    if game['question'][curr] == chars:
        db_game.update_one(
            {},  {"$set": {"answer." + str(curr): str(chars)}})
        db_game.update_one({}, {"$set": {"step": curr+1}})
        db_game.update_one(
            {},  {"$set": {'guessing.' + str(curr): ""}})
    if game['question'][curr] != chars:
        db_game.update_one({},  {"$set": {"fail": fail+1}})
    return gamepage()


@application.route('/gamepage')
def gamepage():
    db_game = db.game
    game = db_game.find_one()
    if game['question'] == game['answer']:
        return win()
    answer = ' '.join(game['answer'])
    guess = ' '.join(game['guessing'])
    body = '<h2 style="color:blue; background-color:tomato; font-size:50px;">Alphabet Guessing Game V.1.0</h2>'
    body += '<h3 style="font-size:20px;">"Please Choose A or B or C or D to guess."</h3>'
    body += '<br>'
    body += 'Answer: ' + answer
    body += '<br> <br>'
    body += 'Character(s) remaining: ' + guess
    body += '<br> <br>'
    body += 'Choose: <button> <a href="/choiceA2">A</a></button> <button> <a href="/choiceB2">B</a></button><button> <a href="/choiceC2">C</a></button> <button> <a href="/choiceD2">D</a></button>'
    body += '<br> <br>'
    body += 'Fails: ' + str(game["fail"])
    return body

@application.route('/win')
def win():
    db_game = db.game
    game = db_game.find_one()
    body = '<h2 style="color:white;background-color:tomato; font-size:50px;" >Alphabet Guessing Game V.1.0</h2>'
    body += '<b >You Win !!!</b>'
    body += '<br> <br> '
    body += '<b>Fails: </b>' + str(game['fail']) + '<b> time(s)</b>'
    body += '<br> <br> '
    db_game = db.game
    database = {
        "question": ["_", "_", "_", "_"],
        "guessing": ["*", "*", "*", "*"],
        "answer": [],
        "fail": 0,
        "step": 0
    }
    db_game.update_one({},  {"$set": database})
    body += '<button> <a href="/">Retry!</a></button>'
    return body


@application.route('/sample')
def sample():
    doc = db.test.find_one()
    # return jsonify(doc)
    body = '<div style="text-align:center;">'
    body += '<h1>Python</h1>'
    body += '<p>'
    body += '<a target="_blank" href="https://flask.palletsprojects.com/en/1.1.x/quickstart/">Flask v1.1.x Quickstart</a>'
    body += ' | '
    body += '<a target="_blank" href="https://pymongo.readthedocs.io/en/stable/tutorial.html">PyMongo v3.11.2 Tutorial</a>'
    body += ' | '
    body += '<a target="_blank" href="https://github.com/andymccurdy/redis-py">redis-py v3.5.3 Git</a>'
    body += '</p>'
    body += '</div>'
    body += '<h1>MongoDB</h1>'
    body += '<pre>'
    body += json.dumps(doc, indent=4)
    body += '</pre>'
    res = redisClient.set('Hello', 'World')
    if res == True:
        # Display MongoDB & Redis message.
        body += '<h1>Redis</h1>'
        body += 'Get Hello => '+redisClient.get('Hello').decode("utf-8")
    return body


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT,
                    debug=ENVIRONMENT_DEBUG)
