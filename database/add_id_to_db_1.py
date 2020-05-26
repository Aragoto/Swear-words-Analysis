import couchdb
import json

couch = couchdb.Server('http://admin:password@localhost:5984')


db = couch['tweet_id']


jsonFile = "city.json"

with open(jsonFile) as f:
    for line in f.readlines():
        try:
            tmp_dic = json.loads(line)
            id = str(tmp_dic["id"])
            db_entry = {}
            record = None
            if tmp_dic["geo"] != "not specified" and tmp_dic["geo"] != None:
                for rec in db.view('tweet_id_record/tweet_id', key = id):
                    record = rec
                if record == None:
                    db_entry["tweet_id"] = id
                    db.save(db_entry)
                else:
                    print(id, ", this tweet has been added to the database!")
                record = None
        except Exception as e:
            print(e)
            continue

