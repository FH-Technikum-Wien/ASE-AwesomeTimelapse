#!/usr/bin/env python3

import pika
import constants
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters(host=constants.HOST_NAME))
channel = connection.channel()
# Create queue to send to, in case it's not created yet (by the receiver).
channel.queue_declare(queue=constants.QUEUE_NAME)
# Send message.
channel.basic_publish(exchange="", routing_key=constants.QUEUE_NAME, body=str(sys.argv[1]))
print(" [x] Message sent!")

connection.close()