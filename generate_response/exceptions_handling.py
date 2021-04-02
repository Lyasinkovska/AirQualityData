import json
import logging

from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import react
from twisted.web.client import BrowserLikePolicyForHTTPS, Agent, readBody
from twisted.web.http_headers import Headers

LOCATIONS_ID = ('72278', '72168', '66213')  # , '70124', '70854', '66076')
BASE_URL = b'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/locations/'
METHOD = b'GET'
HEADERS = {'accept': ['application/json']}

urls = [BASE_URL + location_id for location_id in LOCATIONS_ID]
logging.basicConfig(level=logging.INFO, filename='airquality.log', datefmt='%m-%d-%Y %H:%M', filemode='a',
                    format='%(asctime)s %(message)s')


def get_agent(reactor):
    agent = Agent(reactor, contextFactory=BrowserLikePolicyForHTTPS())
    return agent


@inlineCallbacks
def get_response(reactor, urs):
    agent = get_agent(reactor)
    print 'in get_response'
    for url in urs:
        d_response = yield get_result(agent, url)
        print urls.index(url)
        if d_response:
            read_response_body(d_response)
        else:
            raise Exception('DESTROY ALL LIFE')


@inlineCallbacks
def get_result(agent, url):
    print 'in get result'
    response = yield agent.request(method=METHOD, uri=url, headers=Headers(HEADERS))
    if response.code == 200:
        returnValue(response)
    else:
        raise Exception('DESTROY ALL LIFE')


@inlineCallbacks
def read_response_body(response):
    print 'in read_response_body'
    d_body = yield readBody(response)
    if type(d_body) is str:
        # will become the result of the Deferred
        returnValue(convert_to_json(d_body))
    else:
        # will trigger an errback
        raise Exception('DESTROY ALL LIFE')


@inlineCallbacks
def convert_to_json(body):
    print 'in convert_to_json_body'
    json_res = yield json.loads(body)
    if json_res:
        returnValue(create_data(json_res))
    else:
        raise Exception('DESTROY ALL LIFE')


def create_data(json_res):
    print 'in_create_data'
    try:
        results = json_res.get('results')[0]
        parameters = results.get('parameters')
        params_names = [param.get('displayName') for param in parameters]
        modeling_data = [{'location_name': results.get('name'), 'country': results.get('country'),
                          'coordinates': results.get('coordinates'), 'measured_parameters': params_names}]

        monitoring_data = [{'unit': params.get('unit'), 'param_name': params.get('displayName'),
                            'last_value': params.get('lastValue'),
                            'last_updated': params.get('lastUpdated'), 'parameter_id': params.get('parameterId')} for
                           params
                           in parameters]

        print 'success'

        logging.info('Modeling data: %s\nMonitoring data: %s', modeling_data, monitoring_data)

    except:
        raise Exception('DESTROY ALL LIFE')


# @inlineCallbacks
# def error_handler(error):
#     yield error
#     logging.error('Status code: %s', error)


if __name__ == '__main__':
    react(get_response, argv=(urls,))
