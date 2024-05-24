import pika
import json
import webbrowser
from pysnmp.hlapi import *
from influxdb import InfluxDBClient

INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_DB = 'mydatabase'


def collect_temperature(ip):
    try:
        iterator = getCmd(SnmpEngine(),
                          CommunityData('public'),
                          UdpTransportTarget((ip, 161)),
                          ContextData(),
                          ObjectType(ObjectIdentity('CISCO-ENVMON-MIB', 'ciscoEnvMonTemperatureStatusValue', 1)))

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication:
            print(f"Error: {errorIndication}")
            return None
        elif errorStatus:
            print(f"Error: {errorStatus.prettyPrint()} at {errorIndex and varBinds[int(errorIndex) - 1][0] or '?'}")
            return None
        else:
            for varBind in varBinds:
                return int(varBind[1])
    except Exception as e:
        print(f"Exception during SNMP operation: {e}")
        return None

def save_to_influxdb(switch_id, temperature):  
    try:
        client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT)
        client.switch_database(INFLUXDB_DB)  
        json_body = [
            {
                "measurement": "temperature",
                "tags": {
                    "switch_id": switch_id
                },
                "fields": {
                    "value": temperature
                }
            }
        ]
        client.write_points(json_body)
        print(f"Data successfully written to InfluxDB for switch {switch_id}")
    except Exception as e:
        print(f"Exception during InfluxDB operation: {e}")
        print(json_body)  # Print the JSON body to check its structure
def open_influxdb_web_interface():
    webbrowser.open_new_tab('http://localhost:8086')

def on_message(ch, method, properties, body):
    try:
        task = json.loads(body.decode('utf-8'))  # Ensure decoding the bytes to str
        print(f"Received task: {task}")
        temperature = collect_temperature(task['ip'])
        if temperature is not None:
            save_to_influxdb(task['switch_id'], temperature)  # Adjust the key to 'switch_id'
        else:
            print("Failed to collect temperature")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    except KeyError as e:
        print(f"Missing expected key in task: {e}")
    except Exception as e:
        print(f"Exception in on_message: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='temp_tasks')
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='temp_tasks', on_message_callback=on_message, auto_ack=False)
        print('Waiting for messages. To exit press CTRL+C')
        open_influxdb_web_interface()
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as err:
        print(f"Error connecting to RabbitMQ: {err}")
    except KeyboardInterrupt:
        print("Consumer stopped.")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()

if __name__ == '__main__':
    start_consumer()
