def add_emotion(database, tmp_dic):

    db_entry = {}

    #check emotion class
    if tmp_dic["polarity"] > 0:
        db_entry["emotion"] = "Positive"
    elif tmp_dic["polarity"] < 0:
        db_entry["emotion"] = "Negative"
    else:
        db_entry["emotion"] = "Neutral"
        
    db_entry["city"] = tmp_dic["city"]
        
    database.save(db_entry)
