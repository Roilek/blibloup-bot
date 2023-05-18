import pymongo
import pymongo.errors
import os

from dotenv import load_dotenv

load_dotenv()
MONGO_STR = os.getenv("MONGO_STR")

client = None


def setup():
    global client
    client = connect()
    return


def connect():
    client = pymongo.MongoClient(MONGO_STR)
    return client


def test_connection(client):
    try:
        client.server_info()
        print("Connected to MongoDB!")
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Could not connect to MongoDB.")
    return


def add_user(user_id: int, user_name: str):
    db = client['blibloups']
    user_table = db['users']
    user_table.insert_one({'_id': user_id, 'name': user_name, 'functions': []})
    return


def user_exists(user_id: int) -> bool:
    db = client['blibloups']
    user_table = db['users']
    return user_table.find_one({'_id': user_id}) is not None


def subscribe_user(user_id: int, user_name: str, func: str) -> bool:
    db = client['blibloups']
    user_table = db['users']
    user = user_table.find_one({'_id': user_id})
    if user is None:
        add_user(user_id, user_name)
        user = user_table.find_one({'_id': user_id})
    if func not in user['functions']:
        user['functions'].append(func)
        user_table.update_one({'_id': user_id}, {'$set': {'functions': user['functions']}})
    return True


def unsubscribe_user(user_id: int, func: str) -> bool:
    db = client['blibloups']
    user_table = db['users']
    user = user_table.find_one({'_id': user_id})
    if user is None:
        return False
    if func in user['functions']:
        user['functions'].remove(func)
        user_table.update_one({'_id': user_id}, {'$set': {'functions': user['functions']}})
    return True


def get_subscribed_users(func: str) -> list:
    db = client['blibloups']
    user_table = db['users']
    return [user for user in user_table.find({'functions': func})]


def set_ref_message(name: str, text: str) -> None:
    db = client['blibloups']
    ref_table = db['ref_messages']
    # If name already exists, update text
    if ref_table.find_one({'name': name}) is not None:
        ref_table.update_one({'name': name}, {'$set': {'text': text}})
    else:
        ref_table.insert_one({'name': name, 'text': text})
    return None


def get_ref_message(name: str) -> str:
    db = client['blibloups']
    ref_table = db['ref_messages']
    return ref_table.find_one({'name': name})['text']


if __name__ == "__main__":
    test_connection(connect())


