import json
import time

import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore
from google.cloud import firestore

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "ada-partsDB-firebase-adminsdk.json"

creds = credentials.Certificate('computercompany-64270-firebase-adminsdk.json')
firebase_admin.initialize_app(creds, {
    'databaseURL': 'https://computercompany-64270-default-rtdb.europe-west1.firebasedatabase.app/'
})
firestore_db = firestore.Client()


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
    print("323")
    return False



"""
def get_product_by_id(product_id):
    prd = firestore_db.collection('products').document(product_id).get()
    return prd.to_dict()


def get_all_products_json_fs():
    products = firestore_db.collection('products')
    docs = products.stream()
    prods = dict()
    for doc in docs:
        prods[doc.id] = doc.to_dict()
        print(f'{doc.id} => {doc.to_dict()}')

    return prods


def delete_product_by_id(product_id):
    product = firestore_db.collection('products').document(product_id).delete()
    return


def get_order_by_id(order_id):
    ord = firestore_db.collection('orders').document(order_id).get()
    return ord.to_dict()
"""
