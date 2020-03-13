import flask
import tbroadcast
import etcdbroadcast

app = flask.Flask(__name__)

eb = etcdbroadcast.ETCDBroadcast()
bc = tbroadcast.TBroadcast()
eb._register_northbound(bc)
bc._register_southbound(eb)
bc._start()
eb._start()

@app.errorhandler(Exception)
def all_exception_handler(e):
    return flask.jsonify(error=str(e))

@app.route('/broadcast', methods=['POST'])
def broadcast():
    try:
        messages = flask.request.values.getlist('messages', None)
        return flask.jsonify(result=bc.broadcast(messages)), 200
    except Exception as e:
        return flask.jsonify(error=str(e)), 500

@app.route('/deliver', methods=['GET'])
def deliver():
    try:
        lsn = flask.request.values.get('lsn', None)
        return flask.jsonify(result=bc.deliver(lsn=lsn))
    except Exception as e:
        return flask.jsonify(error=str(e)), 500

@app.route('/ping', methods=['GET'])
def ping():
    return flask.jsonify(result="pong"), 201

@app.route('/info', methods=['GET'])
def info():
    try:
        return flask.jsonify(info=bc.info()), 200
    except Exception as e:
        return flask.jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(port=3489)
    # app.run(debug=True, port=3489)
