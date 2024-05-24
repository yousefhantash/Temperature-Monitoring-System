import pika
import mysql.connector
import json

def get_switches():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="yousef",
            password="ahmad20201965",
            database="mytemp"
        )
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM switches")
        switches = cursor.fetchall()
        cursor.close()
        conn.close()
        return switches
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

def publish_tasks(switches):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='temp_tasks')

        for switch in switches:
            task = json.dumps(switch)
            print(f"Publishing task: {task}")
            channel.basic_publish(exchange='', routing_key='temp_tasks', body=task)

        connection.close()
    except pika.exceptions.AMQPConnectionError as err:
        print(f"Error: {err}")

if __name__ == '__main__':
    switches = get_switches()
    if switches:
        publish_tasks(switches)
    else:
        print("No switches data found or unable to connect to the database.")