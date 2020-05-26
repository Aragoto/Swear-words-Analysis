import couchdb

couch = couchdb.Server('http://admin:password@localhost:5984')

db = couch["dirty_words"]

docs = [{
    "_id": "_design/dirty_words",
    "language" : "javascript",
    "views": {
        "dirty_geo": {
            "map": "function(doc){ emit(doc.city, doc.dirty_words)}",
            "reduce": "function(keys, values, rereduce){ if (rereduce) {return sum(values); } else{ return values.length; }}"
        }
    }
}]

resultList = db.update(docs)
