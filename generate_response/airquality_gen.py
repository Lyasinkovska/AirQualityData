import json
import logging

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import react
from twisted.web.client import BrowserLikePolicyForHTTPS, Agent, readBody
from twisted.web.http_headers import Headers

LOCATIONS_ID = ('70854', '66076', '72278', '72168', '66213', '70124')
BASE_URL = b'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/locations/'
METHOD = b'GET'
HEADERS = {'accept': ['application/json']}
urls = (BASE_URL + location_id for location_id in LOCATIONS_ID)

logging.basicConfig(level=logging.INFO, filename='airquality.log', datefmt='%m-%d-%Y %H:%M', filemode='a',
                    format='%(asctime)s %(message)s')


@inlineCallbacks
def get_response(reactor):
    agent = Agent(reactor, contextFactory=BrowserLikePolicyForHTTPS())
    for url in urls:
        try:
            d_response = yield agent.request(method=METHOD, uri=url, headers=Headers(HEADERS))
        except:
            returnValue('error')
        returnValue(read_response_body(d_response))


@inlineCallbacks
def read_response_body(response):
    d_body = yield readBody(response)
    returnValue(convert_to_json(d_body))


@inlineCallbacks
def convert_to_json(body):
    json_res = yield json.loads(body)
    returnValue(create_data(json_res))


def create_data(json_res):
    results = json_res.get('results')[0]
    parameters = results.get('parameters')
    params_names = [param.get('displayName') for param in parameters]
    modeling_data = {'location_name': results.get('name'), 'country': results.get('country'),
                     'coordinates': results.get('coordinates'), 'measured_parameters': params_names}

    monitoring_data = [{'unit': params.get('unit'), 'param_name': params.get('displayName'),
                        'last_value': params.get('lastValue'),
                        'last_updated': params.get('lastUpdated'), 'parameter_id': params.get('parameterId')} for params
                       in parameters]
    print 'success'

    logging.info('Modeling data: %s\nMonitoring data: %s', modeling_data, monitoring_data)


def error_handler(error):
    print type(error), error
    logging.error('Status code: %s', error)


if __name__ == '__main__':
    react(get_response)
