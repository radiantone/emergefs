from emerge import fs
import emerge.core.objects


class MyClass(emerge.core.objects.EmergeFile):
    """Custom class"""

    def run(self):
        return "words:" + str(self.word_count())

    def word_count(self):
        return len(self.data.split(" "))


""" Store a custom instance there """
obj = MyClass(
    id="myclass",
    name="myclass",
    path="/classes",
    perms="rxwrxwr--",
    data="one two three four",
)
obj.text = "this is myclass of data"

""" Store an object on a specific node """
fs.store(obj)

""" Ask for it back """
obj = fs.getobject("/classes/myclass", False)

""" Execute a method locally on this host """
print("Getting data and word count")
print(obj.data)
print(obj.word_count())
print()

""" Run the object as a service on the remote node """
print("Executing run on server")
print(fs.run("/classes/myclass", "run"))
