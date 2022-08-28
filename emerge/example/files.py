from emerge.core.client import Client
from emerge.core.objects import EmergeFile

""" Connect to specific Node """
client = Client("0.0.0.0", "5558")

""" Store a custom instance there """
obj = EmergeFile(id="file123", name="file 123", path="/files")
obj.data = "this is myclass of data"

""" Store an object on a specific node """
client.store(obj)

""" Ask for it back """
obj = client.get("/files/file 123")
print(obj)

files = client.get("/files")
print(files)
