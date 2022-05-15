import json
import time

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth
from firebase_admin.auth import InvalidIdTokenError
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "computercompany-64270-firebase-adminsdk.json"
os.environ["FIREBASE_WEB_API_KEY"] = "AIzaSyD4L5mu4RnToo3JL-Hz3L_UzR-AuwyVgKI"

creds = credentials.Certificate('computercompany-64270-firebase-adminsdk.json')
fb_admin = firebase_admin.initialize_app(creds)

firestore_db = firestore.Client()


def verify_user_token_admin(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        for user in auth.list_users().iterate_all():
            if user.uid == uid:
                users_data_collection = firestore_db.collection('userData')
                users_data = users_data_collection.stream()
                for user_data in users_data:
                    if user_data.to_dict()["Role"] == "Admin":
                        return True
        return False
    except InvalidIdTokenError:
        return False
    except ValueError:
        return False


def verify_user_token(id_token):
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        for user in auth.list_users().iterate_all():
            if user.uid == uid:
                return True
        return False
    except InvalidIdTokenError:
        return False
    except ValueError:
        return False


"""
def get_all_components_json():
    components = db.reference('components').order_by_key().get()
    print(dict(components))
    return components


def insert_component(comp_info_dict):
    components = db.reference('components')
    new_component = components.push(comp_info_dict)
    return new_component.key


def get_component_by_id(component_id):
    component = db.reference('components').child(component_id).get()
    if component is not None:
        return component
    else:
        return "Not existent in DB!"


def delete_component_by_id(component_id):
    component = db.reference('components').child(component_id).get()
    if component is not None:
        db.reference('components').child(component_id).delete()
        return True
    return False

"""


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
