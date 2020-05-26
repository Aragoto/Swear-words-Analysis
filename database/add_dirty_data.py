import re

def add_dirty(database, tmp_dic, dirty_word):
    dic_tweet = {}
    txt = tmp_dic["text"]
    #lower the words in tweets
    txt = txt.lower()
 
    # use regular expression to split all the punctuation
    # and make the tweet string into word list
    tmp_list = re.findall(r"\w+",txt)

    # this list is used to check if there are same dirty words in the tweet
    added_list = []

    # iterate the tweet word list to check the dirty word
    # if there is dirty word, it would be saved into db
    for word in tmp_list:
        db_entry = {}
        if word in dirty_word.keys() and word not in added_list:
                
            db_entry["dirty_word"] = word
            db_entry["city"] = tmp_dic["city"]
            added_list.append(word)
            database.save(db_entry)
