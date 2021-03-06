import flask
from pika import BlockingConnection, PlainCredentials, ConnectionParameters


class RabbitMQ:

    def __init__(self):
        self.url = flask.current_app.config['INFOSYSTEM_QUEUE_URL']
        self.port = flask.current_app.config['INFOSYSTEM_QUEUE_PORT']
        self.virtual_host = \
            flask.current_app.config['INFOSYSTEM_QUEUE_VIRTUAL_HOST']
        self.username = flask.current_app.config['INFOSYSTEM_QUEUE_USERNAME']
        self.password = flask.current_app.config['INFOSYSTEM_QUEUE_PASSWORD']
        credentials = PlainCredentials(self.username, self.password)
        self.params = ConnectionParameters(
            self.url, self.port, self.virtual_host, credentials)

    def connect(self):
        try:
            return BlockingConnection(self.params)
        except Exception as e:
            raise


class ProducerQueue:

    def __init__(self, exchange, exchange_type):
        rabbitMQ = RabbitMQ()
        self.connection = rabbitMQ.connect()
        self.exchange = exchange
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=exchange, exchange_type=exchange_type, durable=True)

    def publish(self, routing_key):
        body = ""
        self.channel.basic_publish(
            exchange=self.exchange, routing_key=routing_key, body=body)
        self.close()

    def close(self):
        self.channel.close()
        self.connection.close()
