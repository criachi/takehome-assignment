from typing import Tuple

from flask import Flask, jsonify, request, Response
import mockdb.mockdb_interface as db

app = Flask(__name__)

# arg data is a dictionary 
# arg status is an int 
# arg msg is a string
# we know this bc these are type annotations which help w/ code 
# readability and to expect what these args shld be
def create_response(
    data: dict = None, status: int = 200, message: str = ""
) -> Tuple[Response, int]:
    """Wraps response in a consistent format throughout the API.
    
    Format inspired by https://medium.com/@shazow/how-i-design-json-api-responses-71900f00f2db
    Modifications included:
    - make success a boolean since there's only 2 values
    - make message a single string since we will only use one message per response
    IMPORTANT: data must be a dictionary where:
    - the key is the name of the type of data
    - the value is the data itself

    :param data <str> optional data
    :param status <int> optional status code, defaults to 200
    :param message <str> optional message
    :returns tuple of Flask Response and int, which is what flask expects for a response
    """
    if type(data) is not dict and data is not None:
        raise TypeError("Data should be a dictionary 😞")

    response = {
        "code": status,
        "success": 200 <= status < 300,
        "message": message,
        "result": data,
    }
    return jsonify(response), status


"""
~~~~~~~~~~~~ API ~~~~~~~~~~~~
"""


@app.route("/")
def hello_world():
    return create_response({"content": "hello world!"})


@app.route("/mirror/<name>")
def mirror(name):
    data = {"name": name}
    return create_response(data)

@app.route("/shows", methods=['GET'])
def get_all_shows():
    if 'minEpisodes' in request.args:
        minEpisodes = int(request.args.get('minEpisodes'))
    else:
        return create_response({'shows': db.get('shows')})
    newDict = {'shows' : []}
    for i in db.get('shows'):
        if (i["episodes_seen"] >= minEpisodes): 
            newDict['shows'].append(i)
    if newDict['shows']:
        return create_response({"shows": list(newDict.values())})
    return create_response(status=404, message="No show with at least this amount of episodes seen exists")

@app.route("/shows/<id>", methods=['DELETE'])
def delete_show(id):
    if db.getById('shows', int(id)) is None:
        return create_response(status=404, message="No show with this id exists")
    db.deleteById('shows', int(id))
    return create_response(message="Show deleted")



# TODO: Implement the rest of the API here!

@app.route("/shows/<id>", methods =['GET'])
def get_show(id):
    if db.getById('shows', int(id)) is None:
        return create_response(status=404, message="No show with this id exists")
    return create_response(db.getById('shows', int(id)), message="Show returned")

@app.route("/shows", methods =['POST'])
def post_show():
    name = request.form.get('name')
    episodes_seen = request.form.get('episodes_seen')
    if name is None or episodes_seen is None: 
        return create_response(status=422, message="Missing required parameters")
    return create_response(db.create('shows', {"name": name, "episodes_seen": episodes_seen}), status=201)

@app.route("/shows/<id>", methods =['PUT'])
def put_show(id):
    if db.getById('shows', int(id)) is None:
        return create_response(status=404, message="No show with this id exists")
    name = request.form.get('name')
    episodes_seen = request.form.get('episodes_seen')
    if ((name is None) and (episodes_seen is None)): 
        return create_response(db.getById('shows', int(id)), message="Show returned unchanged")
    if name is None:
        return create_response(db.updateById('shows', int(id), {"episodes_seen" : episodes_seen}))
    if episodes_seen is None:
        return create_response(db.updateById('shows', int(id), {"name" : name}))
    return create_response(db.updateById('shows', int(id), {"name" : name, "episodes_seen" : episodes_seen}))


"""
~~~~~~~~~~~~ END API ~~~~~~~~~~~~
"""
if __name__ == "__main__":
    app.run(port=8080, debug=True)
