import configparser
import logging
import os
import sys

import click
from zerorpc.exceptions import RemoteError

logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s: "
    "%(levelname)s: "
    "%(funcName)s(): "
    "%(lineno)d:\t"
    "%(message)s",
)

logger = logging.getLogger(__name__)


def get_methods(file):
    from inspect import signature

    method_list = [
        attribute
        for attribute in dir(type(file))
        if callable(getattr(type(file), attribute))
        and attribute.startswith("_") is False
    ]

    methods = []
    for method in method_list:
        _method = getattr(file, method)
        if _method.__qualname__.find(file.__class__.__name__) == 0:
            methods += [(method, signature(_method))]

    return methods


def human_readable_size(size, decimal_places=2):
    for unit in ["B", "K", "M", "G", "T", "P"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, default=False, help="Debug switch")
@click.option("-h", "--host", default=None, help="hostname:port for node")
@click.pass_context
def cli(context, debug, host):
    """cli base command harness"""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    if debug:
        logging.basicConfig(
            format="%(asctime)s : %(name)s %(levelname)s : %(message)s",
            level=logging.DEBUG,
        )
    else:
        logging.basicConfig(
            format="%(asctime)s : %(name)s %(levelname)s : %(message)s",
            level=logging.INFO,
        )

    from emerge.core.client import Z0RPCClient as Client

    """ Connect to specific Node """

    context.obj = {}

    if host is not None:
        splits = host.split(":")
        context.obj["client"] = Client(splits[0], splits[1])
    else:
        if os.path.exists("emerge.ini"):
            config = configparser.ConfigParser()
            context.obj["config"] = config.read("emerge.ini")
            client = Client(config.get("emerge", "host"), config.get("emerge", "port"))
        else:
            client = Client("0.0.0.0", "5558")

        context.obj["client"] = client
    logging.debug("Debug ON")
    if len(sys.argv) == 1:
        click.echo(context.get_help())


@cli.group()
def node():
    """Emerge node commands"""
    pass


@node.command(name="start")
@click.option("-p", "--port", default=5558, help="Listen port for server")
@click.pass_context
def start(context, port):
    """Start emerge node server"""
    from emerge.node.server import NodeServer

    node = NodeServer(port=port)
    node.setup()
    node.start()


@cli.command()
@click.argument("class1", required=True, default=None)
@click.argument("class2", required=True, default=None)
@click.argument("mixin", required=True, default=None)
@click.argument("name", required=True, default=None)
@click.option("-p", "--path", required=False, default=None)
@click.pass_context
def mixin(context, class1, class2, mixin, name, path):
    """Mix in 2 classes into a new combined class or instance"""
    import json
    import uuid

    client = context.obj["client"]

    _object1 = client.getobject(class1, False)
    _object1_methods = get_methods(_object1)
    _object2 = client.getobject(class2, False)
    _object2_methods = get_methods(_object2)

    _class1 = _object1.__class__
    _class2 = _object2.__class__

    object1_data = json.loads(_object1.to_json())
    object2_data = json.loads(_object2.to_json())
    object1_data.update(object2_data)

    def constructor(self, *args, **kwargs):
        pass

    object1_data["__init__"] = constructor
    # print(_class1,_class2)
    # source = f"""class {mixin}({_class1.__name__},{_class2.__name__}): pass"""
    # print(source)
    # exec(source)

    class EmergeMixin:
        pass

    _mixin = type(mixin, (_class1, _class2, EmergeMixin), object1_data)
    # module = importlib.import_module(_mixin.__module__)
    # setattr(module, name, _mixin)
    help(_mixin)

    mixin_obj = _mixin()

    mixin_obj.id = name
    mixin_obj.name = name
    if path:
        mixin_obj.path = path

        mixin_obj.uuid = str(uuid.uuid4())
        print(mixin_obj)
        # Create instance of __mixin combining the data from object1 and object2
        # inspect.getsource(type(mixin_obj))

        client.store(mixin_obj)
        print("Stored")


@cli.command()
@click.argument("field", required=True, default=None)
@click.argument("query", required=True, default=None)
@click.pass_context
def search(context, field, query):
    """Search for objects by their field data"""
    client = context.obj["client"]

    results = client.searchtext(field, query)

    print(results)


@cli.command()
@click.argument("query", required=False, default=None)
@click.pass_context
def graphql(context, query):
    """Query using graphql"""
    client = context.obj["client"]

    print(client.graphql(query))


@cli.command()
@click.pass_context
def index(context):
    """Create or update a search index"""
    client = context.obj["client"]

    try:
        print("Creating index....")
        client.index()
        print("Index complete.")
    except RemoteError as ex:
        print(ex.msg)


@cli.command()
@click.pass_context
def update(context):
    """Update objects in the database"""
    pass


@cli.command()
@click.argument("path")
@click.pass_context
def rm(context, path):
    """Remove an object or directory"""

    client = context.obj["client"]

    try:
        client.rm(path)
    except RemoteError as ex:
        print(ex.msg)


@cli.command()
@click.argument("directory")
@click.pass_context
def mkdir(context, directory):
    """Make a directory"""
    client = context.obj["client"]
    if directory[0] != "/":
        click.echo("Directory path must be absolute path e.g. /some/dir")
        return

    try:
        client.mkdir(directory)
    except RemoteError as ex:
        print(ex.msg)


@cli.command()
@click.pass_context
def cp(context):
    """Copy object command"""
    pass


@cli.command()
@click.option("-h", "--host", default="0.0.0.0", help="Hostname of server")
@click.option("-p", "--port", default="5558", help="Listen port for server")
def init(host, port):
    """Initialize or update the emerge.ini file"""
    config = configparser.ConfigParser()

    with open("emerge.ini", "w") as fp:
        config.add_section("emerge")
        config.set("emerge", "host", host)
        config.set("emerge", "port", port)
        config.write(fp)

    click.echo("emerge.ini updated.")


@cli.command()
@click.option("-l", "--long", is_flag=True)
@click.argument("directory", default="/")
@click.pass_context
def ls(context, long, directory):
    """List files in a directory"""

    client = context.obj["client"]

    class bcolors:
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKCYAN = "\033[96m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91m"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"

    try:
        files = client.list(directory, offset=0, size=0)
    except RemoteError as ex:
        click.echo(ex.msg)
        return

    logging.debug("FILES:%s", files)
    files = reversed(sorted(files))

    for fname in files:
        if fname.find("dir") == 0:
            if fname == "dir:/" or fname == "dir:/registry":
                continue

            fname = fname.replace("dir:", "")
            logging.debug("Getting fname {}".format(fname))

            file = client.get(fname)
            if "error" in file:
                click.echo(file["message"])
                return

            logging.debug("client.get({}) = {}".format(fname, file))
            row = "{} {: <8} {: >10} {} {} {}".format(
                file["perms"],
                human_readable_size(file["size"], 1)
                if file["type"] == "file"
                else file["size"],
                file["date"],
                bcolors.OKBLUE,
                fname.replace(directory, ""),
                bcolors.ENDC,
            )

            if long:
                print(row)
            else:
                print(fname.replace(directory, ""))
        else:
            file = client.get(fname)
            if type(file) is list:
                pass
            else:
                if "error" in file and file["error"]:
                    click.echo(file["message"])
                    return
                row = "{} {: <8} {: >4} {: >6} {: >4} {: <10}".format(
                    file["perms"],
                    human_readable_size(file["size"], 1)
                    if file["type"] == "file"
                    else file["size"],
                    file["version"],
                    file["date"],
                    bcolors.ENDC,
                    file["name"],
                )

                if long:
                    print(row)
                else:
                    print(file["name"].replace(directory, ""))


@cli.command(name="query")
@click.argument("path")
@click.pass_context
def cmd_query(context, path):
    """Execute query method of an object"""
    client = context.obj["client"]

    results = client.query(path)
    print(results)


@cli.command(name="help")
@click.argument("path")
@click.pass_context
def cmd_help(context, path):
    """Display details of an object class"""
    client = context.obj["client"]

    file = client.getobject(path, False)
    if file is not None:
        help(file)


@cli.command()
@click.argument("path")
@click.pass_context
def methods(context, path):
    """Display available methods for an object"""
    from inspect import signature
    from types import FunctionType

    def listMethods(cls):
        return set(
            x
            for x, y in cls.__dict__.items()
            if isinstance(y, (FunctionType, classmethod, staticmethod))
            and x.startswith("_") is False
            and type(x) is str
        )

    client = context.obj["client"]

    file = client.getobject(path, False)
    if str(file.__class__.__bases__).find("EmergeMixin") > -1:
        for _class in file.__class__.__bases__:
            methods = listMethods(_class)
            if len(list(methods)) > 0:
                mname = list(methods)[0]
                _method = getattr(_class, mname)
                print(mname, str(signature(_method)).replace("self", ""))
    else:
        methods = get_methods(file)
        for method in methods:
            print(method[0], method[1])


@cli.command()
@click.argument("path")
@click.option("-p", "--pretty", is_flag=True)
@click.pass_context
def cat(context, path, pretty):
    """Display contents of an object"""

    client = context.obj["client"]

    file = client.getobject(path, False)

    if not pretty:
        print(file)
    else:
        import json

        try:
            data = json.loads(str(file))
            print(json.dumps(data, indent=4))
        except:
            print(file)


@cli.command()
@click.argument("path")
@click.pass_context
def code(context, path):
    """List source code of an object"""

    client = context.obj["client"]

    file = client.get(path)
    print(file["source"])


@cli.command()
@click.argument("path")
@click.argument("function")
@click.option("-l", "--local", is_flag=True)
@click.pass_context
def call(context, path, function, local):
    """Call an object method"""
    import select
    import sys

    if select.select(
        [
            sys.stdin,
        ],
        [],
        [],
        0.0,
    )[0]:
        data = sys.stdin.read()
    else:
        data = None

    client = context.obj["client"]
    try:
        if local:
            obj = client.getobject(path, False)
            method = getattr(obj, function)
            if data:
                logging.debug("DATA: %s", data)
                print(method(data))
            else:
                print(method())
        else:
            result = client.run(path, function)
            print(result)
    except Exception as ex:
        if hasattr(ex, "msg"):
            logging.error(ex.msg)
        else:
            logging.error(ex)
