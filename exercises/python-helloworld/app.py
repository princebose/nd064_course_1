import json
import logging
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    app.logger.info('Main request successful')
    return "Hello World!"


@app.route("/status")
def status():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Status request successful - Response ({0})'.format(response))
    return response


@app.route("/metrics")
def metrics():
    response = app.response_class(
        response=json.dumps({"status": "success",
                             "code": 0,
                             "data": {"UserCount": 140,
                                      "UserCountActive": 23}}),
        status=200,
        mimetype='application/json'
    )
    app.logger.info('Metrics request successful - Response ({0})'.format(response))
    return response


if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run(host='0.0.0.0')
