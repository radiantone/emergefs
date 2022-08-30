from emerge.core.client import Client
from emerge.core.objects import EmergeFile

""" Connect to specific Node """
client = Client("0.0.0.0", "6558")
""" Store a custom instance there """
obj = EmergeFile(id="file123", name="file 123", path="/files")
obj.data = "this is myclass of data"

""" Store an object on a specific node """
client.store(obj)

""" Ask for it back """
obj = client.get("/files/file 123")
print("OBJ", obj)

files = client.get("/files")
print("FILES", files)

for i in range(0, 10):
    """Store a custom instance there"""
    obj = EmergeFile(id="file" + str(i), name="file " + str(i), path="/files")
    obj.data = "file {} data".format(i)

    """ Store an object on a specific node """
    client.store(obj)

    for x in range(0, 2):
        obj = EmergeFile(
            id="file" + str(i) + ":" + str(x),
            name="file " + str(i) + ":" + str(x),
            path="/files/" + str(i),
        )
        obj.data = "file {}:{} data".format(i, x)

        client.store(obj)

files = client.list("/files/5", offset=0, size=0)
print(files)

objs = [client.get(fid) for fid in files]
print(objs)

# objs = [client.get(fid['path']+"/"+fid['name']) for fid in files]
# for o in objs:
#    print("O:", o)
