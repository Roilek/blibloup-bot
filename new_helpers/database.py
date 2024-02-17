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
        query = {'user_id': sub.user_id, 'name': sub.name}
    elif user_id is not None and name is not None:
        query = {'user_id': user_id, 'name': name}
    else:
        raise ValueError("You have to provide either the user_id and subscription name or a correct Subscription object")

    return subscription_table.find_one(query) is not None

# Create a new subscription for a user
def create_subscription(sub: Subscription) -> bool:
    if subscription_exists(sub=sub):
        return False    
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.insert_one({'user_id': sub.user_id, 'name': sub.name, 'description': sub.description, 'answers': sub.answers, 'frequency': sub.frequency, 'data': sub.data, 'radio': sub.radio, 'state': sub.state})
    return True

# Get a subscription from parameters
def get_subscription_from_param(user_id: int, name: str) -> Subscription:
    db = client['blibloups']
    subscription_table = db['subscriptions']
    sub = subscription_table.find_one({'user_id': user_id, 'name': name})
    return Subscription(sub_dict=sub)

# Get a subscription
def get_subscription(sub: Subscription) -> Subscription:
    return get_subscription_from_param(sub.user_id, sub.name)

# Get subscriptions by frequency
def get_subscriptions_by_frequency(frequency: Frequency) -> list[Subscription]:
    db = client['blibloups']
    subscription_table = db['subscriptions']
    return subscription.list_to_subscriptions(subscription_table.find({'frequency': frequency.value}))

# Get subcriptions by user
def get_subscriptions_by_user(user_id: int) -> list[Subscription]:
    db = client['blibloups']
    subscription_table = db['subscriptions']
    return subscription.list_to_subscriptions(subscription_table.find({'user_id': user_id}))

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

# Update a subscription name
def update_subscription_name(sub: Subscription, name: str) -> Subscription:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.update_one({'user_id': sub.user_id, 'name': sub.name}, {'$set': {'name': name}})
    sub.name = name
    return sub

# Update a subscription description
def update_subscription_description(sub: Subscription, description: str) -> Subscription:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.update_one({'user_id': sub.user_id, 'name': sub.name}, {'$set': {'description': description}})
    sub.description = description
    return sub

# Update a subscription answers
def update_subscription_answers(sub: Subscription, answers: list) -> Subscription:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.update_one({'user_id': sub.user_id, 'name': sub.name}, {'$set': {'answers': answers}})
    sub.answers = answers
    return sub

# Update a subscription frequency
def update_subscription_frequency(sub: Subscription, frequency: str) -> Subscription:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.update_one({'user_id': sub.user_id, 'name': sub.name}, {'$set': {'frequency': frequency}})
    sub.frequency = frequency
    return sub

# Update subscription state
def update_subscription_state(sub: Subscription, state: State) -> Subscription:
    if not subscription_exists(sub=sub):
        return None
    db = client['blibloups']
    subscription_table = db['subscriptions']
    subscription_table.update_one({'user_id': sub.user_id, 'name': sub.name}, {'$set': {'state': state.value}})
    sub.state = state.value
    return True


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

