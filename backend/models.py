from pydantic import BaseModel
from typing import Optional, Union

class ContactCreate(BaseModel):
    name: str
    whatsapp_number: Optional[str] = None
    birthday: Optional[str] = None
    reminder_frequency_days: Union[int, str] = 7
    notes: Optional[str] = None
    last_contact_date: Optional[str] = None
    contact_group: str = 'friends'

class ContactUpdate(BaseModel):
    name: Optional[str] = None
    whatsapp_number: Optional[str] = None
    birthday: Optional[str] = None
    reminder_frequency_days: Optional[Union[int, str]] = None
    notes: Optional[str] = None
    last_contact_date: Optional[str] = None
    contact_group: Optional[str] = None

class ContactLog(BaseModel):
    contact_date: str
    method: str = 'whatsapp'
    notes: Optional[str] = None
