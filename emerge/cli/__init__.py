import logging
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


def human_readable_size(size, decimal_places=2):
    for unit in ["B", "K", "M", "G", "T", "P"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"


@click.group(invoke_without_command=True)
@click.option("--debug", is_flag=True, default=False, help="Debug switch")
@click.pass_context
def cli(context, debug):
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

    from emerge.core.client import Client

    """ Connect to specific Node """
    client = Client("0.0.0.0", "6558")

    context.obj = {}

    context.obj["client"] = client
    logging.debug("Debug ON")
    if len(sys.argv) == 1:
        click.echo(context.get_help())


@cli.group()
def node():
    """Emerge node commands"""
    pass


@node.command(name="start")
@click.option("-p", "--port", default=5558)
@click.pass_context
def start(context, port):
    """Start emerge node server"""
    from emerge.node.server import NodeServer

    node = NodeServer(port=port)
    node.setup()
    node.start()


@cli.command()
@click.pass_context
def rm(context, long, directory):
    """Remove object command"""
    pass


@cli.command()
@click.pass_context
def mkdir(context, long, directory):
    """Make directory command"""
    pass


@cli.command()
@click.pass_context
def cp(context, long, directory):
    """Copy object command"""
    pass


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
                row = "{} {: <8} {: >10} {} {: <10}".format(
                    file["perms"],
                    human_readable_size(file["size"], 1)
                    if file["type"] == "file"
                    else file["size"],
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
    """Display details of an objects class"""
    client = context.obj["client"]

    file = client.getobject(path, False)
    print(help(file))


@cli.command()
@click.argument("path")
@click.pass_context
def methods(context, path):
    """Display available methods for an object"""
    from inspect import signature

    client = context.obj["client"]

    file = client.getobject(path, False)
    method_list = [
        attribute
        for attribute in dir(type(file))
        if callable(getattr(type(file), attribute))
        and attribute.startswith("_") is False
    ]

    for method in method_list:
        print(method, signature(getattr(file, method)))


@cli.command()
@click.argument("path")
@click.pass_context
def cat(context, path):
    """Display contents of an object"""
    client = context.obj["client"]

    file = client.getobject(path, False)
    print(file)


@cli.command()
@click.argument("path")
@click.argument("function")
@click.option("-l", "--local", is_flag=True)
@click.pass_context
def call(context, path, function, local):
    """Call an object method"""
    client = context.obj["client"]

    if local:
        obj = client.getobject(path, False)
        method = getattr(obj, function)
        print(method())
    else:
        result = client.run(path, function)
        print(result)
