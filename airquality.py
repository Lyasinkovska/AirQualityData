import logging
from twisted.internet.task import react
from twisted.web.client import BrowserLikePolicyForHTTPS, Agent, readBody
from twisted.web.http_headers import Headers

LOCATIONS_ID = ('70854', '66076', '72278', '72168', '66213', '70124')
BASE_URL = b'https://u50g7n0cbj.execute-api.us-east-1.amazonaws.com/v2/locations/'
METHOD = b'GET'
HEADERS = {'accept': ['application/json']}
urls = (BASE_URL + location_id for location_id in LOCATIONS_ID)

logging.basicConfig(level=logging.INFO, filename='airquality.log', datefmt='%m-%d %H:%M', filemode='a',
                    format='%(asctime)s %(message)s')


def callback_request(response):
    d = readBody(response)
    d.addCallback(callback_body)
    return d


def callback_body(body):
    logging.info('Response body: %s', body)


def error_handler(error):
    logging.error('Status code: %s', error)


def main(reactor):
    agent = Agent(reactor, contextFactory=BrowserLikePolicyForHTTPS())
    for url in urls:
        d = agent.request(method=METHOD, uri=url, headers=Headers(HEADERS))
        d.addCallbacks(callback_request, error_handler)
    return d


if __name__ == '__main__':
    react(main)
