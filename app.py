import threading

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from DB_interaction import *
from xmlrpc.server import SimpleXMLRPCServer

app = Flask(__name__)
api = Api(app)

component_post_args = reqparse.RequestParser()
component_post_args.add_argument("component_info", type=dict, help="Component info is required!", required=True)


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.localServer = SimpleXMLRPCServer(("127.0.0.1", 2000), logRequests=True)
        prd = Component()
        self.localServer.register_function(prd.get, name="get1")
        lst = Components()
        self.localServer.register_function(lst.get, name="get2")

    def run(self):
        self.localServer.serve_forever()


class Component(Resource):
    def get(self, component_id):
        return get_component_by_id(component_id)

    def delete(self, component_id):
        if delete_component_by_id(component_id):
            return 'success', 200
        else:
            return 'failed', 204


class Components(Resource):
    def get(self):
        return get_all_components_json()

    def post(self):
        args = component_post_args.parse_args()
        component_info = args["component_info"]
        new_comp_id = insert_component(component_info)

        return '' + str(new_comp_id), 201


api.add_resource(Component, '/component/<component_id>')
api.add_resource(Components, '/components')
server = ServerThread()
server.start()


if __name__ == '__main__':
    app.run()



