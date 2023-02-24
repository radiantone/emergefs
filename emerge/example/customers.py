import random
from dataclasses import dataclass
from datetime import date, datetime
from uuid import uuid4
from emerge.core.client import Client
from emerge.core.objects import EmergeFile

client = Client("0.0.0.0", "5558")


@dataclass
class Customer(EmergeFile):
    """A Customer object."""

    createdOn: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    createTimeStamp: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    customerId: str = ''


for i in range(2, 3):
    customerId = str(uuid4())
    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    
    for v in range(0, 3):
        item = Customer(
            id=customerId,
            name="Customer-" + str(i),
            perms="rwxrwxrwx",
            path="/customers",
            data="A customer {} data".format(i),
            customerId=customerId,
            createdOn=now,
            createTimeStamp=now,
            version=v
        )
        print(item)
        client.store(item)
