import threading

from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from flask_httpauth import HTTPTokenAuth
from DB_interaction import *
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler

app = Flask(__name__)
api = Api(app)

auth = HTTPTokenAuth(scheme='Bearer')

component_post_args = reqparse.RequestParser()
component_stock_updt = reqparse.RequestParser()
component_post_args.add_argument("component_info", type=dict, help="Component info is required!", required=True)
component_stock_updt.add_argument("new_stock", type=int, help="New stock is required!", required=True)
port = int(os.environ.get('PORT', 5000))


@auth.verify_token
def verify_token(token):
    if token != "":
        return token


class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/', '/RPC2', '/uuu')


class ServerThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.localServer = SimpleXMLRPCServer(("localhost", 0), logRequests=True, requestHandler=RequestHandler)
        #component = Component()
        #self.localServer.register_function(component.get, name="get1")
        #components = Components()
        #self.localServer.register_function(components.get, name="get2")
        self.localServer.register_introspection_functions()
        self.localServer.register_function(getComponentsInfo, name="getComponentsInfo")
        self.localServer.register_function(areComponentsAvailable, name="areComponentsAvailable")

    def run(self):
        self.localServer.serve_forever()


class Component(Resource):
    def get(self, component_id):
        component = get_component_by_id(component_id)
        if component != "Not existent in DB!":
            return component
        else:
            return "Not existent in DB!", 404

    @auth.login_required
    def delete(self, component_id):
        headers = request.headers
        bearer = headers.get('Authorization')
        tk_type = bearer.split()[0]
        if tk_type == 'Bearer':
            tk = bearer.split()[1]
            if verify_user_token_admin(tk):
                if delete_component_by_id(component_id):
                    return 'success, the component was deleted', 200
                else:
                    return 'failed', 204
            else:
                return 'failed', 204


class Components(Resource):
    def get(self):
        return get_all_components_json()

    @auth.login_required
    def post(self):
        headers = request.headers
        bearer = headers.get('Authorization')
        tk_type = bearer.split()[0]
        if tk_type == 'Bearer':
            tk = bearer.split()[1]
            if verify_user_token_admin(tk):
                args = component_post_args.parse_args()
                component_info = args["component_info"]
                new_comp_id = None
                if component_info is not None:
                    new_comp_id = insert_component(component_info)

                return '' + str(new_comp_id), 201
            else:
                return '', 401
        else:
            return '', 401


class Stock(Resource):
    def get(self, component_id):
        if get_stock_for_component(component_id) != "":
            return get_stock_for_component(component_id)
        else:
            return 'Component not existent!'

    @auth.login_required
    def put(self, component_id):
        headers = request.headers
        bearer = headers.get('Authorization')
        tk_type = bearer.split()[0]
        if tk_type == 'Bearer':
            tk = bearer.split()[1]
            if verify_user_token_admin(tk):
                args = component_stock_updt.parse_args()
                new_stock = args['new_stock']
                return update_stock_for_component(component_id, new_stock)
            else:
                return '', 401
        else:
            return '', 401


#XML_RPC functions
def getComponentsInfo(component_list):
    out_list = list()
    for component in component_list:
        if existing_component(component[0]):
            comp_dict = dict()
            crt_component_info = get_component_by_id(component[0])
            crt_comp_name = crt_component_info['name']
            crt_comp_id = component[0]
            crt_comp_stock = crt_component_info['quantity']

            comp_dict['name'] = crt_comp_name

            if int(crt_comp_stock) == 0:
                comp_dict['isAvailable'] = 'No'
            else:
                if int(crt_comp_stock) >= int(component[1]):
                    comp_dict['isAvailable'] = 'Yes'
                else:
                    comp_dict['isAvailable'] = 'Partially'
            comp_dict['productId'] = crt_comp_id
            out_list.append(comp_dict)
            comp_dict['count'] = crt_comp_stock
    return out_list


def areComponentsAvailable(component_list):
    ok = True
    for component in component_list:
        if existing_component(component[0]):
            crt_component_info = get_component_by_id(component[0])
            crt_comp_stock = crt_component_info['quantity']
            quantity = int(component[1])
            if int(crt_comp_stock) < quantity:
                ok = False
                break

    if ok:
        for component in component_list:
            quantity = int(component[1])
            crt_component_info = get_component_by_id(component[0])
            crt_comp_stock = crt_component_info['quantity']
            update_stock_for_component(component[0], crt_comp_stock - quantity)
        return True
    else:
        return False


api.add_resource(Component, '/component/<component_id>')
api.add_resource(Components, '/components')
api.add_resource(Stock, '/stock/<component_id>')
server = ServerThread()
server.start()

if __name__ == '__main__':
    #app.run(host="0.0.0.0", port=port)
    app.run()
