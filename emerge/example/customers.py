import persistent.list

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from emerge.core.client import Client
from emerge.core.objects import EmergeFile

emerge = Client("0.0.0.0", "5558")

@dataclass
class Customer(EmergeFile):
    """A Customer object."""

    createdOn: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    createTimeStamp: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    customerId: str = ''
    
    fields = persistent.list.PersistentList()
    

if __name__ == '__main__':
    for i in range(0, 100000):
        customerId = str(uuid4())
        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        
        for v in range(0, 4):
            item = Customer(
                id=f"Customer-{i}.{v}",
                name=f"Customer-{i}.{v}",
                perms="rwxrwxrwx",
                path="/customers",
                data=f"A customer {i}.{v} data".format(i),
                customerId=customerId,
                createdOn=now,
                createTimeStamp=now,
                version=v
            )
            print(item)
            emerge.store(item)
