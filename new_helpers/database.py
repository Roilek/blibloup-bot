import pymongo
import pymongo.errors
import os

from dotenv import load_dotenv
from models.enumerations import Frequency, State
from models import subscription
from models.subscription import Subscription


load_dotenv()
MONGO_STR = os.getenv("MONGO_STR")

client = None


# --- CONNECTION ---

# Connect to MongoDB
def connect() -> pymongo.MongoClient:
    global client
    client = pymongo.MongoClient(MONGO_STR)
    return client

# Test connection to MongoDB
def test_connection(client) -> bool:
    try:
        client.server_info()
        print("Connected to MongoDB!")
        return True
    except pymongo.errors.ServerSelectionTimeoutError:
        print("Could not connect to MongoDB.")
    return False


# --- USERS ---

# Check if a user exists
def user_exists(user_id: int) -> bool:
    db = client['blibloups']
    user_table = db['users']
    return user_table.find_one({'_id': user_id}) is not None

# Add a user
def add_user(user_id: int, username: str, first_name: str) -> bool:
    if user_exists(user_id):
        return False
    db = client['blibloups']
    user_table = db['users']
    user_table.insert_one({'_id': user_id, 'username': username, 'first_name': first_name})
    return True

# Delete a user
def delete_user(user_id: int) -> bool:
    if not user_exists(user_id):
        return False
    db = client['blibloups']
    user_table = db['users']
    user_table.delete_one({'_id': user_id})
    return True


# --- SUBSCRIPTIONS ---

# Check if a subscription exists
def subscription_exists(user_id: int = None, name: str = None, sub: Subscription = None) -> bool:
    db = client['blibloups']
    subscription_table = db['subscriptions']

    if sub is not None:
        return subscription_exists(user_id=sub.user_id, name=sub.name)

    return subscription_table.find_one({'user_id': user_id, 'name': name}) is not None

# Create a new subscription for a user
def create_subscription(sub: Subscription) -> bool:
    if subscription_exists(sub=sub):
        return False    
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.insert_one({'user_id': sub.user_id, 'name': sub.name, 'description': sub.description, 'answers': sub.answers, 'frequency': sub.frequency, 'data': sub.data, 'radio': sub.radio, 'state': sub.state})
    return True

# Get a subscription from parameters
def get_subscription(user_id: int = None, name: str = None, sub: Subscription = None) -> Subscription:
    if sub is not None:
        return get_subscription(user_id=sub.user_id, name=sub.name)
    db = client['blibloups']
    subscription_table = db['subscriptions']
    sub = subscription_table.find_one({'user_id': user_id, 'name': name})
    return Subscription(sub_dict=sub) if sub is not None else None

# Get subscriptions by frequency
def get_subscriptions(user_id: int = None, frequency: Frequency = None) -> list[Subscription]:
    db = client['blibloups']
    subscription_table = db['subscriptions']
    query = {}
    if user_id is not None:
        query['user_id'] = user_id
    if frequency is not None:
        query['frequency'] = frequency.value
    return subscription.list_to_subscriptions(subscription_table.find(query))

# Delete a subscription from parameters
def delete_subscription_from_parameters(user_id: int, name: str) -> bool:
    
    if not subscription_exists(user_id=user_id, name=name):
        return False
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.delete_one({'user_id': user_id, 'name': name})
    return True

# Delete a subscription
def delete_subscription(sub: Subscription) -> bool:
    return delete_subscription_from_parameters(sub.user_id, sub.name)

# Update a subscription
def update_subscription(sub: Subscription, new_name: str = None, new_description: str = None, new_answers: list[str] = None, new_frequency: Frequency = None, new_radio: bool = None, new_state: State = None) -> Subscription:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    query = {}
    name = sub.name
    if new_name is not None:
        query['name'] = new_name
        sub.name = new_name
    if new_description is not None:
        query['description'] = new_description
        sub.description = new_description
    if new_answers is not None:
        query['answers'] = new_answers
        sub.answers = new_answers
    if new_frequency is not None:
        query['frequency'] = new_frequency.value
        sub.frequency = new_frequency.value
    if new_radio is not None:
        query['radio'] = new_radio
        sub.radio = new_radio
    if new_state is not None:
        query['state'] = new_state.value
        sub.state = new_state.value
    subscription_table.update_one({'user_id': sub.user_id, 'name': name}, {'$set': query})
    return sub

# --- SUBSCRIPTION ANSWERS ---

# Update the data field of a subscription to add a pair of date with the chosen options
def update_data(sub: Subscription, date: str, chosen: str) -> list[str]:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    data = get_data(sub, date)
    # if chosen was already in the list, remove it, otherwise add it
    # TODO outsource logic to Subscription class
    if data is None:
        data = [chosen]
    elif chosen in data:
        data.remove(chosen)
    elif sub.radio:
        data = [chosen]
    else:
        data.append(chosen)
    subscription_table.update_one({'user_id': sub.user_id, 'name': sub.name}, {'$set': {f'data.{date}': data}})
    return data

# Get the data field of a subscription for a given date
def get_data(sub: Subscription, date: str) -> list[str]:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    return subscription_table.find_one({'user_id': sub.user_id, 'name': sub.name})['data'].get(date, [])


if __name__ == "__main__":
    connect()
    test_connection(client)

