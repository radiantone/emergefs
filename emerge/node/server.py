import logging

from emerge.core.objects import Server


class NodeServer(Server):
    topic = "NODE"
    socket = None
    port = "5557"

    def shutdown(self) -> bool:
        logging.debug("[NodeServer] shutdown...")
        return True

    def stop(self) -> bool:
        logging.debug("[NodeServer] stop...")
        self.thread.join()
        return True

    def setup(self, options: dict = {}) -> bool:
        import threading

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

        self.thread = threading.Thread(target=get_messages)
        self.thread.start()
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
        return True
