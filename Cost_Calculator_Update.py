import firebase_admin
from firebase_admin import credentials, db

# Initialize the app with your service key and database URL
databaseURL = {'databaseURL': 'https://costcalculator-bd26f-default-rtdb.firebaseio.com'}
cred = credentials.Certificate('serviceAK.json')
firebase_admin.initialize_app(cred, databaseURL)

# Get a reference to the database
ref = db.reference('py/Transactions/01022023083827')

# Query for the documents you want to update
results = ref.order_by_child('Category').equal_to('Other Bills').get()
print(results)

# Update the documents
#field_updates = {'Category': 'Fun'}
#for key in results:
#    ref.child(key).update(field_updates)
