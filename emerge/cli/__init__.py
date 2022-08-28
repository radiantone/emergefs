import logging
import sys

import click

logging.basicConfig(
    level=logging.INFO,
    format="%(filename)s: "
    "%(levelname)s: "
    "%(funcName)s(): "
    "%(lineno)d:\t"
    "%(message)s",
)

logger = logging.getLogger(__name__)


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
    client = Client("0.0.0.0", "5558")

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
@click.pass_context
def start(context):
    """Start emerge node server"""
    from emerge.node.server import NodeServer

    node = NodeServer()
    node.setup()
    node.start()


def human_readable_size(size, decimal_places=2):
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if size < 1024.0 or unit == "PiB":
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"


@cli.command()
@click.argument("directory", default="/")
@click.pass_context
def ls(context, directory):
    """List files in a directory"""

    client = context.obj["client"]

    files = client.list(directory, offset=0, size=0)
    for fname in files:
        file = client.get(fname)
        row = "{: <8} {: >10} {: <10}".format(
            human_readable_size(file["size"], 1), file["date"], file["name"]
        )
        print(row)


@cli.command()
@click.argument("path")
@click.pass_context
def cat(context, path):
    """Display contents of a file"""
    client = context.obj["client"]

    file = client.get(path)
    print(file)
