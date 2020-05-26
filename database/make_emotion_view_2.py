import couchdb

couch = couchdb.Server('http://admin:password@localhost:5984')

db = couch["emotion"]

docs = [{
    "_id": "_design/emotion_classify",
    "language" : "javascript",
    "views": {
        "emotion": {
            "map": "function(doc){ emit([doc.city, doc.emotion], 1)}",
            "reduce": "function(keys, values, rereduce){ if (rereduce) {return sum(values); } else{ return values.length; }}"
        }
    }
}]

resultList = db.update(docs)
