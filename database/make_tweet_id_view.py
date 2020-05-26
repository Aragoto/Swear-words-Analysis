import couchdb

couch = couchdb.Server('http://admin:password@localhost:5984')

db = couch["tweet_id"]

docs = [{
    "_id": "_design/tweet_id_record",
    "language" : "javascript",
    "views": {
        "tweet_id": {
            "map": "function(doc){ emit(doc.tweet_id, 1)}"
        }
    }
}]

resultList = db.update(docs)
