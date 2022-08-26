import logging
import signal
from typing import List

from emerge.core.objects import Server
from emerge.fs.filesystem import FileSystemFactory


class NodeServer(Server):
    """Node server"""

    topic = "NODE"
    socket = None
    port = "5557"

    services: List = []

    def shutdown(self) -> bool:
        logging.debug("[NodeServer] shutdown...")
        [service.shutdown() for service in self.services]
        return True

    def stop(self) -> bool:
        logging.debug("[NodeServer] stop...")
        self.process.terminate()

        [service.stop() for service in self.services]

        return True

    def setup(self, options: dict = {}) -> bool:
        import multiprocessing

        import zmq

        logging.debug("[NodeServer] Setup...")

        # Socket to talk to server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        host = "127.0.0.1"
        port = "5557"

        self.socket.connect("tcp://{}:{}".format(host, port))

        self.socket.subscribe("NODE")
        logging.debug("Subscribed to NODE")

        def get_messages():
            while True:
                logging.debug("get_messages")
                logging.debug("Waiting on message")
                string = self.socket.recv_string()
                logging.debug("Got message %s", string)
            logging.debug("Quitting get_messages")

        self.process = multiprocessing.Process(target=get_messages)
        self.process.start()

        fs = FileSystemFactory.get()
        self.services += [fs]

        [service.setup() for service in self.services]

        def handler(signum, frame):
            self.stop()
            self.shutdown()

        signal.signal(signal.SIGINT, handler)  # type: ignore

        return True

    def start(self) -> bool:
        import time

        import zmq

        logging.debug("[NodeServer] start...")

        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://127.0.0.1:%s" % "5557")

        time.sleep(1)

        # Receives a string format message
        socket.send_string("NODE hi")

        [service.start() for service in self.services]

        return True
