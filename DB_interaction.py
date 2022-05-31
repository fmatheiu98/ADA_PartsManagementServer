import json
import time

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError
from google.cloud import firestore
import requests
import pjrpc
from pjrpc.client.backend import requests as pjrpc_client


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "computercompany-64270-firebase-adminsdk.json"
os.environ["FIREBASE_WEB_API_KEY"] = "AIzaSyD4L5mu4RnToo3JL-Hz3L_UzR-AuwyVgKI"

creds = credentials.Certificate('computercompany-64270-firebase-adminsdk.json')
fb_admin = firebase_admin.initialize_app(creds)

firestore_db = firestore.Client()

asm_client = pjrpc_client.Client('https://server-asm-ada.herokuapp.com/api/json-rpc/server')

def existing_component(component_id):
    comp = firestore_db.collection('components').document(component_id).get()
    if comp.to_dict() is not None:
        return True
    return False


def verify_user_token_admin(id_token):
    try:
        #uid = requests.get('https://server-asm-ada.herokuapp.com/intraserver/getId', data={'token': id_token}).text
        uid = (asm_client.send(pjrpc.Request('getUserID', params=[id_token], id=1))).result

        for user in auth.list_users().iterate_all():
            if user.uid == uid:
                """
                users_data_collection = firestore_db.collection('userData')
                users_data = users_data_collection.stream()
                for user_data in users_data:
                    if user_data.to_dict()["Role"] == "Admin":
                        return True
                """
                #isAdmin = requests.get('https://server-asm-ada.herokuapp.com/intraserver/isAdmin', data={'token': id_token}).text
                isAdmin = (asm_client.send(pjrpc.Request('isUserAdmin', params=[id_token], id=1))).result
                if isAdmin == True:
                    return True
        return False
    except ExpiredIdTokenError:
        return False
    except InvalidIdTokenError:
        return False
    except ValueError:
        return False


def verify_user_token(id_token):
    try:
        #uid = requests.get('https://server-asm-ada.herokuapp.com/intraserver/getId', data={'token': id_token}).text
        uid = (asm_client.send(pjrpc.Request('getUserID', params=[id_token], id=1))).result

        for user in auth.list_users().iterate_all():
            if user.uid == uid:
                return True
        return False
    except ExpiredIdTokenError:
        return False
    except InvalidIdTokenError:
        return False
    except ValueError:
        return False


def get_component_by_id(component_id):
    comp = firestore_db.collection('components').document(component_id).get()
    if comp.to_dict() is not None:
        return comp.to_dict()
    else:
        return "Not existent in DB!"


def get_all_components_json():
    components = firestore_db.collection('components')
    docs = components.stream()
    comps = dict()
    for doc in docs:
        comps[doc.id] = doc.to_dict()

    if len(comps) != 0:
        return comps
    else:
        return "No components in the DB!"


def get_all_components_with_type_json(component_type):
    components = firestore_db.collection('components')
    docs = components.stream()
    comps = dict()
    for doc in docs:
        specs = doc.to_dict()['specifications']
        if specs['type'] == component_type:
            comps[doc.id] = doc.to_dict()
    if len(comps) != 0:
        return comps
    else:
        return "No components with that type in the DB!"


def insert_component(comp_info_dict):
    components = firestore_db.collection('components')
    new_component = components.add(comp_info_dict)
    return new_component[1].id


def delete_component_by_id(component_id):

    component = firestore_db.collection('components').document(component_id).get()
    if component.to_dict() is not None:
        firestore_db.collection('components').document(component_id).delete()
        return True
    return False


def get_stock_for_component(component_id):
    component = firestore_db.collection('components').document(component_id).get()
    comp_info_dict = component.to_dict()
    if comp_info_dict is not None:
        return comp_info_dict['quantity']
    return ""


def update_stock_for_component(component_id, new_stock):
    component = firestore_db.collection('components').document(component_id).get()
    if component.to_dict() is not None:
        comp = firestore_db.collection('components').document(component_id)
        comp.update({'quantity': new_stock})
        return True
    return False


def dict_traverse(comp_dict, comparing_dict):
    for key, value in comp_dict.items():
        if type(value) is dict:
            if key not in comparing_dict:
                comparing_dict[key] = dict()
                for k, v in value.items():
                    if k not in comparing_dict[key]:
                        comparing_dict[key][k] = []
            else:
                for k, v in value.items():
                    if k not in comparing_dict[key]:
                        comparing_dict[key][k] = []
        else:
            if key not in comparing_dict:
                comparing_dict[key] = []
    return comparing_dict


def populate_comparison_dict(comparing_dict, c_dict1, c_dict2):
    for key, value in comparing_dict.items():
        if type(value) is dict:
            for k, v in value.items():
                if k in c_dict1[key] and k in c_dict2[key]:
                    comparing_dict[key][k] = [c_dict1[key][k], c_dict2[key][k]]
                elif k in c_dict1[key] and k not in c_dict2[key]:
                    comparing_dict[key][k] = [c_dict1[key][k], ""]
                elif k not in c_dict1[key] and k in c_dict2[key]:
                    comparing_dict[key][k] = ["", c_dict2[key][k]]
        else:
            if key in c_dict1 and key in c_dict2:
                comparing_dict[key] = [c_dict1[key], c_dict2[key]]
            elif key in c_dict1 and key not in c_dict2:
                comparing_dict[key] = [c_dict1[key], ""]
            elif key not in c_dict1 and key in c_dict2:
                comparing_dict[key] = ["", c_dict2[key]]

    return comparing_dict


def compare_components_func(component1_id, component2_id):
    component1 = firestore_db.collection('components').document(component1_id).get()
    component2 = firestore_db.collection('components').document(component2_id).get()

    result = None
    if component1.to_dict() is not None and component2.to_dict() is not None:
        comp1_specs = component1.to_dict()['specifications']
        comp2_specs = component2.to_dict()['specifications']

        if comp1_specs['type'] == comp2_specs['type']:
            res1 = dict_traverse(comp1_specs, dict())
            res2 = dict_traverse(comp2_specs, res1)
            result = populate_comparison_dict(res2, comp1_specs, comp2_specs)
            result['name'] = [component1.to_dict()['name'], component2.to_dict()['name']]
            result['price'] = [component1.to_dict()['price'], component2.to_dict()['price']]
            result['stock'] = [component1.to_dict()['quantity'], component2.to_dict()['quantity']]
        else:
            return {"components not of the same type!": ""}
    return result


