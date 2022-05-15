import threading

from flask import Flask, request
from flask_restful import reqparse, abort, Api, Resource
from flask_httpauth import HTTPTokenAuth
from DB_interaction import *
from xmlrpc.server import SimpleXMLRPCServer

app = Flask(__name__)
api = Api(app)

auth = HTTPTokenAuth(scheme='Bearer')

component_post_args = reqparse.RequestParser()
component_post_args.add_argument("component_info", type=dict, help="Component info is required!", required=True)

tokens = {
    "eyJhbGciOiJSUzI1NiIsImtpZCI6ImJlYmYxMDBlYWRkYTMzMmVjOGZlYTU3ZjliNWJjM2E2YWIyOWY1NTUiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vY29tcHV0ZXJjb21wYW55LTY0MjcwIiwiYXVkIjoiY29tcHV0ZXJjb21wYW55LTY0MjcwIiwiYXV0aF90aW1lIjoxNjUyNjM0Nzk2LCJ1c2VyX2lkIjoiRmxxOXhia1lZYU5INlBNOTY2c25GR21SWFhuMiIsInN1YiI6IkZscTl4YmtZWWFOSDZQTTk2NnNuRkdtUlhYbjIiLCJpYXQiOjE2NTI2MzQ3OTYsImV4cCI6MTY1MjYzODM5NiwiZW1haWwiOiJ0ZXN0NEB0ZXN0LmNvbSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJ0ZXN0NEB0ZXN0LmNvbSJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.Ei7iKTxzrTenSpcJq3xzU7sCgtfp2jIgBBEmf1OlCHuUTMRDZ2AsmdYYw983erRE3w57npKJlk9bu22oHcW5CL5TE78n6vor7-TujRQpDDyKW9YVoQRnHTANgNZrZ0TzvX5Y4Ikuqb3dsBvMYavFPDM0ghrWVZlYDysQ6jMdssYIfiaWKh08jT_eJct6xldIXj6AK0jTvqYhLV5kBCR5TRMbi6rjqbZ0ka5DzpPoh1PcyzhdvAwj62YxxCUOtKjpoqyiBkOv8CebHOA4PVzHA8ZPkCybZ7I7Vu2YtEjUtE76KNJDP5_3WAb-eWJoNeXBx0OUZbavS-8ToxxiJdB5wQ": "john"
}


@auth.verify_token
def verify_token(token):
    if token != "":
        return token


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


api.add_resource(Component, '/component/<component_id>')
api.add_resource(Components, '/components')

#server = ServerThread()
#server.start()


if __name__ == '__main__':
    app.run()



