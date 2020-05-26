import couchdb
import json
import re

couch = couchdb.Server('http://admin:password@localhost:5984')

#db = couch["test1"]
db_new = couch['emotion']

emotion = {}
d_list = []

jsonFile = "city.json"

num = 0
num_line = 0
num_sub = 0
with open(jsonFile) as f:
    for line in f.readlines():
        num_line += 1
        try:
            tmp_dic = json.loads(line)
            dic_tweet = {}

            #只选有sub信息的tweet
            if tmp_dic["city"] != "not specified" and tmp_dic["city"] != None:
               # num_sub += 1
                db_entry = {}

                #判断情感
                if tmp_dic["polarity"] > 0:
                    dic_tweet["emotion"] = "Positive"
                elif tmp_dic["polarity"] < 0:
                    dic_tweet["emotion"] = "Negative"
                else:
                    dic_tweet["emotion"] = "Neutral"
                db_entry["city"] = tmp_dic["city"]
                db_entry["emotion"] = dic_tweet["emotion"]
                num += 1
                db_new.save(db_entry)
        except Exception as e:
            pass
            continue
