from datetime import datetime
from models.enumerations import Frequency, State

class Subscription:
    user_id: int
    name: str
    description: str
    answers: list[str]
    frequency: int
    radio: bool
    data: dict
    state: State

    def __init__(self, user_id: int = None, name: str = None, description: str = None, answers: list[str] = None, frequency: int = None, radio: bool = True, state: State = None, sub_dict: dict = None):
        if sub_dict is not None:
            self.user_id = sub_dict['user_id']
            self.name = sub_dict['name']
            self.description = sub_dict['description']
            self.answers = sub_dict['answers']
            self.frequency = sub_dict['frequency']
            self.radio = sub_dict['radio']
            self.state = sub_dict['state']
            self.data = sub_dict['data']
        else:
            self.user_id = user_id
            self.name = name
            self.description = description
            self.answers = answers
            self.frequency = frequency
            self.radio = radio        
            self.state = state
            self.data = {}

    def subcription_to_database(self) -> dict:
        return {
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'answers': self.answers,
            'frequency': self.frequency,
            'radio': self.radio,
            'data': self.data,
            'state': self.state
        }
        
    
def list_to_subscriptions(subs: list[dict]) -> list[Subscription]:
    return [Subscription(sub_dict=sub) for sub in subs]