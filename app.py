from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, date
from urllib.parse import quote_plus
from time import strftime
# from dotenv import load_dotenv
import os
import pymongo
from pymongo import MongoClient
app = Flask(__name__)

 
 
uri = 'mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false'
client = MongoClient(uri)




 
# client = MongoClient(host='test_mongodb',
#                          port=27017, 
#                          username='root', 
#                          password='pass',
#                         authSource="admin")

# client

try:
    # Attempt to connect to the MongoDB database
    client.server_info()
    print("Successfully connected to the database.")
except Exception as e:
    # Print the error message and exit the program
    print("Failed to connect to the database.")
    print(e)
    exit()

# connect to MongoDB
# client = pymongo.MongoClient()
db = client.test
user_collection = db.users

# create a user document with current date and time
user = {
    'name': 'John',
    'date_of_birth': "1990-05-21",
    'created_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
}

# insert the user document into the collection
result = user_collection.insert_one(user)
print(result.inserted_id)

@app.route('/', methods=['GET'])
def home():
    return 'hello world'

@app.route('/users/<string:name>', methods=['PUT'])
def update_user(name):
    # check if the name contains only letters
    if not name.isalpha():
        return 'Invalid name', 400
    
    # find the user by name in the database
    user = user_collection.find_one({'name': name})
    
    # if the user is not found, return a 404 error
    if user is None:
        return 'User not found', 404
    
    # get the new name and date of birth from the request body
    new_name = request.json.get('name')
    new_date_of_birth = request.json.get('date_of_birth')
    
    # validate the new date of birth
    if new_date_of_birth:
        try:
            new_date_of_birth = datetime.strptime(new_date_of_birth, '%Y-%m-%d')
            if new_date_of_birth >= datetime.today():
                return 'Invalid date of birth', 400
        except ValueError:
            return 'Invalid date of birth', 400
    
    # update the user's name and date of birth in the database
    update = {}
    if new_name:
        update['name'] = new_name
    if new_date_of_birth:
        update['date_of_birth'] = new_date_of_birth.strftime('%Y-%m-%d')
    user_collection.update_one({'name': name}, {'$set': update})
    
    # return a 204 No Content response
    return '', 204

@app.route('/users/<string:name>', methods=['GET'])
def get_birthday_message(name):
    # find the user by name in the database
    user = user_collection.find_one({'name': name})
    
    # if the user is not found, return a 404 error
    if user is None:
        return 'User not found', 404
    
    # calculate the number of days until the user's birthday
    today = datetime.today()
    print(today)

    birthday = datetime.strptime(user['date_of_birth'], '%Y-%m-%d')
    print(birthday)

    birthday_this_year = birthday.replace(year=today.year)
    print(today)

    if birthday_this_year < today:
        birthday_this_year = birthday_this_year.replace(year=today.year + 1)
    days_until_birthday = (birthday_this_year - today).days
    
    # generate the birthday message
    if days_until_birthday == 0:
        message = f'Hello, {name}! Happy birthday!'
    else:
        message = f'Hello, {name}! Your birthday is in {days_until_birthday}  day(s) and the time is:  {today}'
        # The_time_is = f"{birthday_this_year}"
        # return (The_time_is)
    
    # return the message as JSON
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
