#!/home/nischal/naxa/nginx_log/bin/python

from prometheus_client import start_http_server, REGISTRY
from prometheus_client.core import GaugeMetricFamily
import time
import os
from ast import literal_eval

# define a custom collector to handle the nginx metrics
class NginxCollector(object):
    def collect(self):
        # create a gauge metric family for each metric we want to expose
        resp_body_size = GaugeMetricFamily('nginx_resp_body_size', 'Response body size', labels=['source', 'host', 'uri', 'status'])
        request_length = GaugeMetricFamily('nginx_request_length', 'Request length', labels=['source', 'host', 'uri', 'status'])
        resp_time = GaugeMetricFamily('nginx_resp_time', 'Response time', labels=['source', 'host', 'uri', 'status'])
        
        # read the data from the follow_log generator
        for line_as_dict in follow_log('/home/nischal/naxa/nginx_log/src/test'):
            resp_body_size.add_metric([line_as_dict['source'], line_as_dict['host'], line_as_dict['uri'], line_as_dict['status']], line_as_dict['resp_body_size'])
            request_length.add_metric([line_as_dict['source'], line_as_dict['host'], line_as_dict['uri'], line_as_dict['status']], line_as_dict['request_length'])
            resp_time.add_metric([line_as_dict['source'], line_as_dict['host'], line_as_dict['uri'], line_as_dict['status']], line_as_dict['resp_time'])
        
        # return the metric families as a list
        return [resp_body_size, request_length, resp_time]

# read the data from the follow_log generator
def follow_log(file):
    with open(file, 'r') as f:
        f.seek(0, os.SEEK_END)
        # infinite loop
        while True:
            line = f.readlines()
            if not line:
                time.sleep(0.1)
                continue
            
            line = line[1]
            line = line.strip("\n")
            line_as_dict = literal_eval(line)
            yield line_as_dict

# register the custom collector with the registry
REGISTRY.register(NginxCollector())

# start the HTTP server to expose the metrics
start_http_server(8000)

# loop forever to keep the program running
while True:
    time.sleep(1)
