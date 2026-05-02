import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

# Path to your Firebase service account key JSON
FIREBASE_KEY_PATH = os.path.join(os.path.dirname(__file__), "..", "firebase_config.json")

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_KEY_PATH)
    firebase_admin.initialize_app(cred)

# Firestore client (you can now use db in allocator.py or app.py)
db = firestore.client()

# --------------------
# User-related helpers
# --------------------

def add_user(uid, username, password):
    """
    Store a new user in Firestore under 'users' collection.
    (Currently stores password in plain text — recommend hashing later)
    """
    user_ref = db.collection("users").document(uid)
    user_ref.set({
        "username": username,
        "password": password,
    })
    return True

def get_user(username, password):
    users_ref = db.collection("users")
    query = users_ref.where("username", "==", username).where("password", "==", password).limit(1).stream()

    for user in query:
        return user.id, user.to_dict()
    return None, None

def add_expense(user_id, date, description, amount, category):
    expense_ref = db.collection("users").document(user_id).collection("expenses").document()
    expense_ref.set({
        "date": date,
        "description": description,
        "amount": amount,
        "category": category
    })
    return True

def get_expenses(user_id):
    expenses_ref = db.collection("users").document(user_id).collection("expenses").order_by("date", direction=firestore.Query.DESCENDING)
    return [doc.to_dict() for doc in expenses_ref.stream()]
