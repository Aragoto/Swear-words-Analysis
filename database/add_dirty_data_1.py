import couchdb
import json
import re


couch = couchdb.Server('http://admin:password@localhost:5984')

#db = couch["test1"]
db_new = couch['dirty_words']

dirty_word = {}
d_list = []

with open("list.txt") as f:
    for line in f.readlines():
        d_list.append(line)
f.close()

# 一个脏词的字典 value均为[] 主要用于查询key是否存在 所以value不重要
for word in d_list:
    word = word.strip('\n')
    dirty_word[word] = 0

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
            if tmp_dic["city"] != "not specified" and tmp_dic["city"] != "":
                num_sub += 1

                txt = tmp_dic["text"]
                txt = txt.lower() #将tweet单词变为小写
                tmp_list = re.findall(r"\w+",txt)#将tweet变为单词list

                added_list = []
                for word in tmp_list:
                    db_entry = {}
                    if word in dirty_word.keys() and word not in added_list:
                        #dic_tweet["dirty_word"].append(word)
                        db_entry["dirty_word"] = word
                        db_entry["city"] = tmp_dic["city"]
                        added_list.append(word)
                        num += 1
                        db_new.save(db_entry)
        except Exception as e:
            continue

print(num)
