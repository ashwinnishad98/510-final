import firebase_admin
from firebase_admin import credentials, firestore


# init Firebase
def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase.json")
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    return db
