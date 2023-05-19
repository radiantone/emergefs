import random
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

import persistent.list

import emerge.core.objects
from emerge import fs

versions = False


@emerge.dataclass
class CustomerHelper(emerge.core.objects.EmergeFile):
    def dedupe(self, fs=None):
        from collections import defaultdict

        _versions = defaultdict(list)
        for customer in fs.dir("/customers"):
            _versions[customer.customerId].append(customer)

        dupes = 0

        for key, versions in _versions.items():
            _dupes = [
                item
                for item in versions
                if item not in [max(versions, key=lambda o: o.version)]
            ]
            dupes += len(_dupes)
            [fs.rm(version.path + "/" + version.name) for version in _dupes]

        return f"{dupes} versions removed."


helper = CustomerHelper(
    id="CustomerHelper", name="CustomerHelper", perms="rwxrwxrwx", path="/helpers"
)


fs.store(helper)


@dataclass
class Customer(emerge.core.objects.EmergeFile):
    """A Customer object."""

    words: list = field(default_factory=list)
    createdOn: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    createTimeStamp: str = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    customerId: str = ""
    value: int = 0
    fields = persistent.list.PersistentList()

    def getId(self):
        return self.customerId


_words = ["one", "two", "three", "four", "five"]

for i in range(0, 20):
    customerId = str(uuid4())
    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    words = []
    words += [_words[random.randrange(len(_words))]]
    words += [_words[random.randrange(len(_words))]]
    item = Customer(
        id=f"Customer-{i}",
        name=f"Customer-{i}",
        words=words,
        perms="rwxrwxrwx",
        path="/customers",
        value=random.randrange(10),
        data=f"A customer {i} data".format(i),
        customerId=customerId,
        createdOn=now,
        createTimeStamp=now,
        version=0,
    )
    print(item)
    fs.store(item)

if versions:
    for i in range(0, 100):
        customerId = str(uuid4())
        now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

        for v in range(0, 4):
            item = Customer(
                id=f"Customer-{i}.{v}",
                name=f"Customer-{i}.{v}",
                words=["one", "two", "three", "four", "five"],
                perms="rwxrwxrwx",
                path="/customers",
                value=random.randrange(10),
                data=f"A customer {i}.{v} data".format(i),
                customerId=customerId,
                createdOn=now,
                createTimeStamp=now,
                version=0,
            )
            print(item)
            fs.store(item)
