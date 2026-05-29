import json


def create_message(message_type, sender, content):
    message = {
        "type": message_type,
        "sender": sender,
        "content": content
    }

    return (json.dumps(message) + "\n").encode()


def parse_message(message):
    return json.loads(message.decode())