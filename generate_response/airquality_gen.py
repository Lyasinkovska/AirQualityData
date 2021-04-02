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


def main(twisted_agent, generated_urls):
    deferred_lst = []
    for url in generated_urls:
        try:
            d = getResponse(twisted_agent, url)
            deferred_lst.append(d)
        except Exception, e:
            print(e)
    list_deferred = DeferredList(deferred_lst, consumeErrors=True)
    list_deferred.addBoth(lambda shutdown: reactor.stop())


def error(reason):
    logging.error(reason.value)


@inlineCallbacks
def getResponse(twisted_agent, url):
    try:
        response = yield twisted_agent.request(method=METHOD, uri=url, headers=Headers(HEADERS)).addErrback(error)
    except Exception, e:
        print(e)
    else:
        readResponseBody(response)


@inlineCallbacks
def readResponseBody(response):
    try:
        body = yield readBody(response)
    except Exception, e:
        print(e)
    else:
        convertToJson(body)


def convertToJson(body):
    parseData(json.loads(body))


def parseData(json_res):
    try:
        results = json_res.get('results')[0]
        logging.info(results.get("name"))
        parameters = results.get('parameters')
    except Exception, e:
        raise e
    else:
        saveModelingData(results, parameters)
        saveMonitoringData(results, parameters)


def saveModelingData(results, parameters, fp=fp_modeling):
    params_names = [param.get("displayName") for param in parameters]
    modeling_data = {"{}".format(results.get("name")): {"country": results.get("country"),
                                                        "coordinates": results.get("coordinates"),
                                                        "measured_parameters": params_names}
                     }
    writeJson(fp, modeling_data)


def saveMonitoringData(results, parameters, fp=fp_monitoring):
    monitoring_data = {}
    for param in parameters:
        monitoring_data["{}".format(results.get("name"))] = {"unit": param.get("unit"),
                                                             "param_name": param.get("displayName"),
                                                             "last_value": param.get("lastValue"),
                                                             "last_updated": param.get("lastUpdated"),
                                                             "parameter_id": param.get("parameterId")}
    writeJson(fp, monitoring_data)


def readJson(filename='modeling_data.json'):
    with open(filename, 'r') as read_file:
        downloaded_file = json.load(read_file)
        return downloaded_file


def writeJson(filename, data):
    try:
        downloaded_file = readJson(filename)
        downloaded_file.append(data)
    except ValueError:
        downloaded_file = [data]
    with open(filename, 'w') as data_file:
        json.dump(downloaded_file, fp=data_file, indent=2, encoding='utf-8')


if __name__ == '__main__':
    agent = Agent(reactor, contextFactory=BrowserLikePolicyForHTTPS())
    main(agent, urls)
    reactor.run()
