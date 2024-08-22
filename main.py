import os
import tinytuya
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import datetime
import logging


def fetch_and_store_data():
    c = tinytuya.Cloud(
        apiKey=os.environ.get('TUYA_APIKEY'),
        apiSecret=os.environ.get('TUYA_APISECRET'),
        apiRegion=os.environ.get('TUYA_APISREGION')
    )

    url = os.environ.get('INFLUXDB_URL')
    token = os.environ.get('INFLUXDB_TOKEN')
    org = os.environ.get('INFLUXDB_ORG')
    bucket = os.environ.get('INFLUXDB_BUCKET')
    client = InfluxDBClient(url=url, token=token)

    devices = c.getdevices()
    write_api = client.write_api(write_options=SYNCHRONOUS)

    for device in devices:
        print("Name: %s, ID: %s" % (device['name'], device['id']))
        status = c.getstatus(device['id'])

        temperature = None
        humidity = None

        for result in status['result']:
            if result['code'] == 'va_humidity':
                humidity = result['value']
            if result['code'] == 'va_temperature':
                temperature = result['value']

        if temperature is not None and humidity is not None:
            point = Point("SonOff Humidity / Temperature") \
                .tag("location", device['name']) \
                .field("temperature", temperature) \
                .field("humidity", humidity) \
                .time(datetime.datetime.now(datetime.UTC), WritePrecision.NS)

            write_api.write(bucket=bucket, org=org, record=point)
            print("Data for device %s written successfully" % device['name'])
        else:
            print("Skipping device %s due to missing temperature or humidity data" % device['name'])

    client.close()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def handler(event, context):
    try:
        fetch_and_store_data()
        logger.info('Data fetching and storage complete.')
        return {
            'statusCode': 200,
            'body': 'Data fetching and storage complete.'
        }
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
