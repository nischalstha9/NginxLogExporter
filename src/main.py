#!/home/nischal/naxa/nginx_log/bin/python
import os
from ast import literal_eval
import time
from prometheus_client import start_http_server, Summary
from prometheus_client.core import GaugeMetricFamily, REGISTRY

BASE_DIR=os.path.dirname(os.path.realpath(__file__))
SEEK_FILE=os.path.join(BASE_DIR,"exporter-data","seek_index")

LOG_FILE_DIR="NginxExporterLogStorage"
LOG_FILE_NAME=os.environ.get("LOG_FILE_NAME","test")


def write_seek(seek):
    f = open(SEEK_FILE, "w")
    f.write(str(seek))
    f.close()

def get_seek():
    try:
        f = open(SEEK_FILE, "r")
        num = int(f.readline().strip())
        f.close()
        return num
    except:
        f = open(SEEK_FILE, "w")
        f.write(str(0))
        f.close()
        return 0


class NGINXCollector(object):
    def __init__(self):
        pass

    def collect(self):
        file_path = os.path.join(BASE_DIR,LOG_FILE_DIR, LOG_FILE_NAME)
        resp_body_size = GaugeMetricFamily('nginx_resp_body_size', 'Response body size', labels=['host', 'uri', 'status'])
        request_length = GaugeMetricFamily('nginx_request_length', 'Request length', labels=['host', 'uri', 'status'])
        resp_time = GaugeMetricFamily('nginx_resp_time', 'Response time', labels=['host', 'uri', 'status'])

        start_seek = get_seek()
        with open(file_path, 'r') as f:
            lines=f.readlines()
            end_seek = len(lines)
            if end_seek > start_seek:
                lines = lines[start_seek:end_seek+1]
                write_seek(end_seek)
                start_seek = end_seek
                for line in lines:
                    line = line.strip()
                    line_as_dict = literal_eval(line)
                    resp_body_size.add_metric([line_as_dict['host'], line_as_dict['uri'], str(line_as_dict['status'])], str(line_as_dict['resp_body_size']))
                    request_length.add_metric([line_as_dict['host'], line_as_dict['uri'], str(line_as_dict['status'])], str(line_as_dict['request_length']))
                    resp_time.add_metric([line_as_dict['host'], line_as_dict['uri'], str(line_as_dict['status'])], str(line_as_dict['resp_time']))
            else:
                pass

            yield resp_body_size
            yield request_length
            yield resp_time



# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)


if __name__ == "__main__":
    port = 8000
    REGISTRY.register(NGINXCollector())
    start_http_server(port)
    print(f"Nginx Prometheus Exporter metrics available at: http://0.0.0.0:{port}")
    while True: 
        time.sleep(10)