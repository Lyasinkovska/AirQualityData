import json
import logging

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.web.client import BrowserLikePolicyForHTTPS, Agent, readBody
from twisted.web.http_headers import Headers

fp_monitoring = 'monitoring_data.json'
fp_modeling = 'modeling_data.json'
LOCATIONS_ID = ('72278', '72168', '66213', '70124', '70854', '66076')
BASE_URL = b'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/locations/'
METHOD = b'GET'
HEADERS = {'accept': ['application/json']}
urls = (BASE_URL + location_id for location_id in LOCATIONS_ID)
logging.basicConfig(level=logging.INFO, filename='airquality.log', datefmt='%y-%m-%d %H:%M', filemode='a',
                    format='%(asctime)s %(message)s')


def main(agent, urls):
    dl = []
    for url in urls:
        try:
            d = get_response(agent, url)
            dl.append(d)
        except Exception, e:
            print e
    list_deferred = DeferredList(dl, consumeErrors=True)
    list_deferred.addBoth(lambda shutdown: reactor.stop())


def error(reason):
    logging.error(reason.value)


@inlineCallbacks
def get_response(agent, url):
    try:
        response = yield agent.request(method=METHOD, uri=url, headers=Headers(HEADERS)).addErrback(error)
    except Exception, e:
        print e
    else:
        read_response_body(response)


@inlineCallbacks
def read_response_body(response):
    try:
        body = yield readBody(response)
    except Exception, e:
        print e
    else:
        convert_to_json(body)


def convert_to_json(body):
    create_data(json.loads(body))


def create_data(json_res):
    try:
        results = json_res.get('results')[0]
        logging.info(results.get("name"))
        parameters = results.get('parameters')
    except Exception, e:
        raise e
    else:
        save_modeling_data(results, parameters)
        save_monitoring_data(results, parameters)
    return 'Done'


def save_modeling_data(results, parameters, fp=fp_modeling):
    params_names = [param.get("displayName") for param in parameters]
    modeling_data = {"{}".format(results.get("name")): {"country": results.get("country"),
                                                        "coordinates": results.get("coordinates"),
                                                        "measured_parameters": params_names}
                     }
    write_to_json(fp, modeling_data)


def save_monitoring_data(results, parameters, fp=fp_monitoring):
    monitoring_data = {
        "{}".format(results.get("name")): {"unit": params.get("unit"), "param_name": params.get("displayName"),
                                           "last_value": params.get("lastValue"),
                                           "last_updated": params.get("lastUpdated"),
                                           "parameter_id": params.get("parameterId")} for params
        in parameters
    }

    write_to_json(fp, monitoring_data)


def read_json(filename='modeling_data.json'):
    with open(filename, 'r') as read_file:
        file = json.load(read_file)
        return file


def write_to_json(filename, data):
    try:
        file = read_json(filename)
        file.append(data)
    except:
        file = [data]
    with open(filename, 'w') as data_file:
        json.dump(file, fp=data_file, indent=2, encoding='utf-8')


if __name__ == '__main__':
    agent = Agent(reactor, contextFactory=BrowserLikePolicyForHTTPS())
    main(agent, urls)
    reactor.run()
