from enum import Enum

class Frequency(Enum):
    SECONDLY = 'Secondly'
    MINUTELY = 'Minutely'
    HOURLY = 'Hourly'
    DAILY = 'Daily'
    WEEKLY = 'Weekly'
    MONTHLY = 'Monthly'
    YEARLY = 'Yearly'

class State(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'