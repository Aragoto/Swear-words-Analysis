import couchdb
import json
from add_dirty_data import add_dirty 
from add_emotion_data import add_emotion

# connect to localhost couchDB
couch = couchdb.Server('http://admin:password@localhost:5984')

# get the databases
db_id = couch['tweet_id']
db_dirty = couch["dirty_words"]
db_emotion = couch["emotion"]

# get the dirty word list
d_list = []
with open("list.txt") as f:
    for line in f.readlines():
        d_list.append(line)
f.close()

# make the dirty word list into dictionary to improve the search efficiency
dirty_word = {}
for word in d_list:
    word = word.strip('\n')
    dirty_word[word] = 0

# get the json file of processed local data
jsonFile = "city.json"

# read file line by line
with open(jsonFile) as f:
    for line in f.readlines():
        try:
            # store each line as a temporary dictionary
            tmp_dic = json.loads(line)

            # tweet_id is needed to force transform into string format
            # if use tweet id as number directly
            # cuouchDB can not distinguish  
            tweet_id = str(tmp_dic["id"])

            # db_entry is the dic that is going to be saved in db_id 
            db_entry = {}

            # record have to be voided before iterate the view
            # because if there is no value, then record would not be passed
            record = None

            # check if city value is valid
            if tmp_dic["city"] != "not specified" and tmp_dic["city"] != None:

                # check if the tweet id have been already in the id database 
                for rec in db_id.view('tweet_id_record/tweet_id', key = tweet_id):
                    record = rec

                # if the tweet id is not in the id database
                # record would be none
                # then we can use this tweet 
                # and store the related infomation into databases
                if record == None:
                    db_entry["tweet_id"] = tweet_id

                    # save id into id db
                    db_id.save(db_entry)
                    # save dirty words and city into dirty db
                    add_dirty(db_dirty, tmp_dic, dirty_word)
                    # save emotion and city into emotion db
                    add_emotion(db_emotion, tmp_dic)
                else:
                    # if record is not none
                    # the tweet is duplicate then pass
                    print(tweet_id, ", this tweet has been added to the database!")
                record = None
        except Exception as e
            continue

