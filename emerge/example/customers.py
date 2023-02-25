import persistent.list

from dataclasses import dataclass
from datetime import date, datetime
from uuid import uuid4

from emerge.core.client import Client
from emerge.core.objects import EmergeFile
from emerge.core.decorators import filesystem

emerge = Client("0.0.0.0", "5558")

@dataclass
class CustomerHelper(EmergeFile):
    
    def dedupe(self, fs=None):
        from collections import defaultdict

        _versions = defaultdict(list)
        for customer in fs.dir("/customers"):
            _versions[customer.customerId].append(customer)
        
        dupes = 0

        for key, versions in _versions.items():
            _dupes = [item for item in versions if item not in [max(versions, key=lambda o: o.version)]]
            dupes += len(_dupes)
            [fs.rm(version.path+"/"+version.name) for version in _dupes]
            
        return f"{dupes} versions removed."
    
helper = CustomerHelper(
    id=f"CustomerHelper",
    name=f"CustomerHelper",
    perms="rwxrwxrwx",
    path="/helpers")


emerge.store(helper)
            
@dataclass
class Customer(EmergeFile):
    """A Customer object."""

    createdOn: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    createTimeStamp: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    customerId: str = ''
    
    fields = persistent.list.PersistentList()
    

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
