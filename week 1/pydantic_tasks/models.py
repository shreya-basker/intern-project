from pydantic import BaseModel,ConfigDict, AfterValidator, Field, ValidationError, field_validator, model_validator
from typing import Annotated,List
from datetime import datetime,timezone,date
def verify_age(age: int )->int:
    if age<18 or age>100:
        raise ValueError("Age must be between 18 and 100")
    return age
class User(BaseModel):
    id : int
    name: str
    email: str
    @field_validator("email")
    @classmethod
    def email_validation(cls, email: str)->str :
        if "@"  not in email or "." not in email:
            raise ValueError("@ or . not present. Not valid")
        return email


    age : Annotated[int, AfterValidator(verify_age)]
    created_at : datetime = Field(default_factory= lambda : datetime.now(timezone.utc))
    addresses : List[Address]
class Optional(BaseModel):
    id: int
    name: str='Jane Doe'
    # id is non optional which means the Model will raise a Validation Error
    # name will not raise any error, instead it will use the default given during Model creation


class Event(BaseModel):
    start_date : date
    end_date : date
    @model_validator(mode='after')
    def event_validator(self)-> 'Event':
        if self.start_date>self.end_date:
            raise ValueError("End date before Start Date. Not valid")
        return self

class Address(BaseModel):
    street : str
    city : str
    postcode : int


# ------------- OUTPUTS ----------------------

# Valid User Data
try:
    valid_user=User(
        id=123,
        name = "James",
        email = "james@gmail.com",
        age= 25
    )
    print("Model instantiated successfully!")
    print("User data:",valid_user.model_dump()) # .model_dump() -> shows all data in a dict format
except ValidationError as e:
    print("Model failed at validation",e)

# Invalid User Data
try:
    invalid_user=User(
        id=223,
        email = "james@gmail.com",
        age= 15
    )
except ValidationError as e:
    print("Model failed at validation")
    for error in e.errors():
        print(f"error msg : {error['msg']}")
        print(f"error type : {error['type']}")

# Optional Data 
try :
    user=Optional(id=123)
    print("Model created successfully")
    print("User data :",user.model_dump())
except ValidationError as e:
    print("Model Failed",e)

try:
    in_user=Optional(
        name='James'
    )
except ValidationError as e:
    print("Model failed at validation")
    for error in e.errors():
        print(f"Error type: {error['type']}")
        print(f"Error msg : {error['msg']}")

#email checking
user=User(
    id=101,
    name='Shreya',
    email="shreyagmail.com",
    age=20
)

#event checking
event=Event(
    start_date="2026-06-10",
    end_date="2026-05-10"
)

#address insertion
user1 = User(
    id=101,
    name="Shreya",
    email="shreya@gmail.com",
    age=20,
    addresses=[
        Address(
            street="123 MG Road",
            city="Bangalore",
            postcode="560001"
        ),
        Address(
            street="45 Brigade Road",
            city="Bangalore",
            postcode="560025"
        )
    ]
)

print(user)
