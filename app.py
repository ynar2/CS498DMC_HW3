from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.read_preferences import ReadPreference
from pymongo.write_concern import WriteConcern

app = Flask(__name__)

# Connect to MongoDB Atlas Replica Set using your cluster details
MONGO_URI = "mongodb+srv://new_user3:YOUR_PASSWORD@lab6cluster.epcwk6x.mongodb.net/?retryWrites=true&w=majority&appName=Lab6Cluster"
client = MongoClient(MONGO_URI)
db = client["ev_db"]
collection = db["vehicles"]

@app.route("/insert-fast", methods=["POST"])
def insert_fast():
    data = request.json
    # Write Concern: Acknowledges write from PRIMARY node only (w=1)
    wc_collection = collection.with_options(write_concern=WriteConcern(w=1))
    result = wc_collection.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)}), 201

@app.route("/insert-safe", methods=["POST"])
def insert_safe():
    data = request.json
    # Write Concern: Ensures write to the majority of replica set members (w='majority')
    wc_collection = collection.with_options(write_concern=WriteConcern(w="majority"))
    result = wc_collection.insert_one(data)
    return jsonify({"inserted_id": str(result.inserted_id)}), 201

@app.route("/count-tesla-primary", methods=["GET"])
def count_tesla_primary():
    # Strongly consistent read: strictly from primary node
    rp_collection = collection.with_options(read_preference=ReadPreference.PRIMARY)
    count = rp_collection.count_documents({"Make": "TESLA"})
    return jsonify({"count": count}), 200

@app.route("/count-bmw-secondary", methods=["GET"])
def count_bmw_secondary():
    # Eventually consistent read: read from secondary, fallback to primary if secondary fails
    rp_collection = collection.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED)
    count = rp_collection.count_documents({"Make": "BMW"})
    return jsonify({"count": count}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
