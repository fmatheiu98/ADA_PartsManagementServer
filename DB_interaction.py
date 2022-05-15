import json
import time

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "computercompany-64270-firebase-adminsdk.json"

creds = credentials.Certificate('computercompany-64270-firebase-adminsdk.json')
firebase_admin.initialize_app(creds, {
    'databaseURL': 'https://computercompany-64270-default-rtdb.europe-west1.firebasedatabase.app/'
})

firestore_db = firestore.Client()

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
