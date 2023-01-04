from emerge.core.client import Client
from emerge.core.objects import EmergeFile


class MyClass(EmergeFile):
    """Custom class"""

    def run(self):
        return "wordsA:" + str(self.word_count())

    def word_count(self):
        return len(self.data.split(" "))


""" Connect to specific Node """
client = Client("0.0.0.0", "6558")

""" Store a custom instance there """
obj = MyClass(id="myclass", name="myclass", path="/classes", perms="rxwrxwr--", data="one two three four")
obj.text = "this is myclass of data"

""" Store an object on a specific node """
client.store(obj)

""" Ask for it back """
obj = client.getobject("/classes/myclass")

""" Execute a method locally on this host """
print("Getting data and word count")
print(obj.data)
print(obj.word_count())
print()

""" Run the object as a service on the remote node """
print("Executing run on server")
print(client.run("/classes/myclass", "run"))

