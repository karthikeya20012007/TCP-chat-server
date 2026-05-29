import json


def create_message(message_type, sender, content):
    return json.dumps({
        "type": message_type,
        "sender": sender,
        "content": content
    }).encode()


def parse_message(message):
    return json.loads(message.decode())