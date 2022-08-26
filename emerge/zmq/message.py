from emerge.zmq.connection import redis_connection


def get_topic_msg_key(topic, msg_id, delimiter=":"):
    key = "TOPIC{delimiter}{topic}{delimiter}MESSAGE{delimiter}{msg_id}".format(
        topic=topic, msg_id=msg_id, delimiter=delimiter
    )
    return key


def get_topic_msg_read_key(topic, msg_id, sub_id, delimiter=":"):
    key = "SUBSCRIBER{delimiter}{sub_id}{delimiter}READ{delimiter}TOPIC{delimiter}{topic}{delimiter}MESSAGE{delimiter}{msg_id}".format(
        topic=topic, msg_id=msg_id, sub_id=sub_id, delimiter=delimiter
    )
    return key


def get_topic_key_pattern(topic, delimiter=":"):
    key = "TOPIC{delimiter}{topic}{delimiter}MESSAGE{delimiter}*".format(
        topic=topic, delimiter=delimiter
    )
    return key


def extract_msg_id_from_topic_msg_key(topic_msg_key):
    return topic_msg_key[topic_msg_key.rfind(":") + 1 :]


def write_msg(topic, msg_id, msg, ttl=180):
    msg_key = get_topic_msg_key(topic, msg_id)
    redis_connection.set(msg_key, msg)
    redis_connection.expire(msg_key, ttl)


def get_msg(topic, msg_id):
    msg_key = get_topic_msg_key(topic, msg_id)
    msg = redis_connection.get(msg_key)
    return msg


def get_msg_by_key(topic_msg_key):
    return redis_connection.get(topic_msg_key)


def pop_msg(topic, msg_id):
    msg_key = get_topic_msg_key(topic, msg_id)
    msg = redis_connection.get(msg_key)
    redis_connection.delete(msg_key)
    return msg


def mark_msg_as_read(topic, msg_id, sub_id):
    topic_msg_read_key = get_topic_msg_read_key(topic, msg_id, sub_id)
    msg_key = get_topic_msg_key(topic, msg_id)
    redis_connection.set(topic_msg_read_key, 1)
    redis_connection.expire(topic_msg_read_key, redis_connection.ttl(msg_key))


def is_msg_read(topic, msg_id, sub_id):
    topic_msg_read_key = get_topic_msg_read_key(topic, msg_id, sub_id)
    return redis_connection.get(topic_msg_read_key) is not None


def get_msgs_for_topic(topic):
    topic_key_pattern = get_topic_key_pattern(topic)
    yield from redis_connection.scan_iter(match=topic_key_pattern, count=100)
