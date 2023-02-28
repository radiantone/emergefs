
from dataclasses import dataclass
from datetime import date, datetime
from uuid import uuid4

from emerge.core.client import Client
from emerge.core.objects import EmergeFile

emerge = Client("0.0.0.0", "5558")


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