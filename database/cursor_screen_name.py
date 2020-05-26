import tweepy
from tweepy.streaming import StreamListener

from tweepy import OAuthHandler
from tweepy import Stream
import json as js
import argparse
import datetime
import couchdb
from textblob import TextBlob
from shapely.geometry import Point, Polygon
import time
import re
import argparse
import socket


cities = ["Ballarat", "Banyule", "Baw Baw", "Bayside", "Benalla", "Boroondara", "Brimbank", "Campaspe",
"Cardinia", "Casey", "Colac-Otway", "Corangamite", "Darebin", "East Gippsland", "Frankston", "Greater Shepparton",
"Hobsons Bay", "Kingston", "Knox", "Latrobe", "Loddon", "Macedon Ranges", "Manningham",
"Maribyrnong", "Maroondah", "Melbourne", "Melton", "Mildura", "Mitchell", "Moira", "Monash", "Moreland", "Mornington Peninsula",
"Mount Alexander", "Nillumbik", "Northern Grampians", "Port Phillip", "Pyrenees", "South Gippsland", "Southern Grampians",
"Stonnington", "Glen Eira", "Greater Bendigo", "Greater Dandenong", "Greater Geelong", "Glenelg", "Surf Coast", "Swan Hill",
"Wangaratta", "Warrnambool", "Wellington", "Whitehorse", "Wodonga", "Wyndham", "Yarra", "Yarra Ranges"]

with open('suburb-geo-lga-new.json') as suburb_file:
    #process polygon file to generate a polygon dict to use
    suburb_list = js.load(suburb_file)
    for suburb in suburb_list:
        if suburb['polygon']:
            polygon = []
            for coor in suburb['polygon']:
                polygon.append(tuple(coor))
            suburb['polygon'] = polygon

print('preporcessed')

def argsnb():
    #deploy nginx and node
    FLAG = argparse.ArgumentParser(description='servers')
    FLAG.add_argument('--nginx')
    FLAG.add_argument('--backup1')
    FLAG.add_argument('--backup2')
    arguments = FLAG.parse_args()
    return arguments

def GetDirtyList():
    #generate dirty word dict
    dirty_word = {}
    d_list = []

    with open("list.txt") as f:
        for line in f.readlines():
            d_list.append(line)
    f.close()

    for word in d_list:
        word = word.strip('\n')
        dirty_word[word] = 0
    
    return dirty_word   

nodes = argsnb()
    
#connect to couchdb, and try another gate if one failed
try:
    couch = couchdb.Server('http://admin:password@localhost:5984')
except:
    try: 
        couch = couchdb.Server('http://admin:password@'+nodes.nginx+':5984')
    except:
        try:
            couch = couchdb.Server('http://admin:password@'+nodes.backup1+':5984')
        except:
            try:
                couch = couchdb.Server('http://admin:password@'+nodes.backup2+':5984')
            except Exception as e:
                print("Can not access to the database! \n Please Check your internet.")
db_dirty = couch["dirty_words"]
db_emotion = couch["emotion"]
db_id = couch["tweet_id"]
dirty_word_dic = GetDirtyList()

def in_suburb(longitude, latitude, suburb):
    #match the polygon to suburb, as the polygon map is provided in suburb level
    point = Point(longitude, latitude)
    polygon = Polygon(suburb['polygon'])
    return point.within(polygon)


def coor_to_city(longitude, latitude, row):
    #use polygon map to match the coordinate to city
    city = ""
    for suburb in suburb_list:
        if in_suburb(longitude, latitude, suburb):
            city = suburb['lga_name']
            break
    return city

#set the credentials into lists, call them iteratively
consumer_key = ['6ETA0Zjw2bS7htWkcwYsmY4kA', 'mLE5EPHyhF5V19V0SLALg75Kj', 'KkBDT4dOceWxhGHp74rXUfg94']
consumer_secret = ['chJp4AxFAhikIWXnJ2wIq4zqaXtygARIKcbyNJa67PH7NwDiww', 'X4PiePNaxqEiNcneh1XxPyoEQ9oMbWG3dZEk7EYgdPm8vKf2UE', '0ZHuXmYEO5KiJGajvoV6aNIXmxsm3BmTOEq9VydiCKntJX76E5']
access_token = ['1251842554141618176-BCDBIcPK3Zx5SpyOrMGS01N4vk2dEg', '3401543464-JvCeSmLjLZFGwSKWZDDwcFH7RJLULbrVhoR0uCz', '1250618520771035136-A6IthX5Ub82m3SPQbeA8ZpvBsJhh4G']
access_secret = ['aGru0K5H08XE3Ddr4S2od84eFXKdtxNQwBn4rI3AVcevc', '7xqyLryUNWSNylEavarSCsYiiLHFzV8BwaWekgTMJImfY', 'CMk5eTGG2HwFM2fhU9fCD7blUJCNzguwSjlSh2qczwmqs']
key = iter(consumer_key)
secret = iter(consumer_secret)
token = iter(access_token)
a_secret = iter(access_secret)

auth = tweepy.auth.OAuthHandler(next(key), next(secret))
auth.set_access_token(next(token), next(a_secret))
api = tweepy.API(auth)

#verify the credential is valid or not
try:
    api.verify_credentials()
    print("verified credential")
except:
    print("error in credential")

def get_tweets(tweetJson, dirty_word_dic):
    #process the qualified tweet to normalized data
    dataDict = {}
    if tweetJson['full_text']:
        text = tweetJson['full_text']
        dataDict['text'] = text
        blob = TextBlob(text)
        dataDict['polarity'] = blob.sentiment.polarity
        #generate the sentiment of the text
        dataDict['id'] = tweetJson['id']
        if tweetJson['coordinates']:
            #coordinates to city
            longitude = tweetJson['coordinates']['coordinates'][0]
            latitude = tweetJson['coordinates']['coordinates'][1]
            ct = coor_to_city(longitude, latitude, tweetJson)
            try:
                if ct in cities:
                    if tweetJson['place']:
                        dataDict['geo'] = tweetJson['place']['name']
            except TypeError:
                print(tweetJson['place']['name'])
                pass
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'poi':
            #bounding box to city
            longitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][0] + tweetJson['place']['bounding_box']['coordinates'][0][2][0])/2
            latitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][1] + tweetJson['place']['bounding_box']['coordinates'][0][1][1])/2
            if longitude != 145.0531355 and latitude != -37.9725665:
                    ct = coor_to_city(longitude, latitude, tweetJson)
                    if ct in cities:
                        dataDict['geo'] = ct
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'city':
            #city information stored by tweet
            if tweetJson['place']['name'] in cities:
                dataDict['geo'] = tweetJson['place']['name']
        else:
            dataDict['geo'] = "not specified"

        print(dataDict)
        print("*****************************************")
        CheckTweetID_And_AddToDB(dataDict)
        


def DirtyWordProcess(dataDict):
    #get the dirty words of tweets by regular expression, store them to couchdb
    tmp_dic = dataDict
    if tmp_dic["geo"] != None and tmp_dic["geo"] != "not specified" and  tmp_dic["geo"] != "" and tmp_dic["geo"] != None:
        txt = tmp_dic["text"]
        txt = txt.lower() 
        tmp_list = re.findall(r"\w+",txt)
        added_list = []
        for word in tmp_list:
            db_entry = {}
            if word in dirty_word_dic.keys() and word not in added_list:
                db_entry["dirty_word"] = word
                db_entry["city"] = tmp_dic["geo"]
                added_list.append(word)
                db_dirty.save(db_entry)
            else:
                pass


def EmotionProcess(dataDict):
    #transform polarity to positive, negative and neutral, and save to couchdb
    tmp_dic = dataDict
    if tmp_dic["geo"] != None and tmp_dic["geo"] != "not specified" and  tmp_dic["geo"] != "" and tmp_dic["geo"] != None:
        #check the geo information is not empty
        db_entry = {}
        dic_tweet = {}
        if tmp_dic["polarity"] > 0:
            dic_tweet["emotion"] = "Positive"
        elif tmp_dic["polarity"] < 0:
            dic_tweet["emotion"] = "Negative"
        else:
            dic_tweet["emotion"] = "Neutral"
        db_entry["city"] = tmp_dic["geo"]
        db_entry["emotion"] = dic_tweet["emotion"]
        db_emotion.save(db_entry)

def CheckTweetID_And_AddToDB(dataDict):
    #chech the tweet with same id have saved in couchdb or not, to decide whether this tweet to upload or not
    tmp_dic = dataDict
    id = str(tmp_dic["id"])
    db_entry = {}
    record = None
    if tmp_dic["geo"] != "not specified" and tmp_dic["geo"] != None:
        #check the geo information is not empty
        for rec in db_id.view('tweet_id_record/tweet_id', key = id):
            record = rec
        if record == None:
            db_entry["tweet_id"] = id
            db_id.save(db_entry)
            EmotionProcess(dataDict)
            DirtyWordProcess(dataDict)
        else:
            print(id, ", this tweet's information has been added to the database!")

    

maxid = None
tweecount = 0
i = 0
start = [None]*len(consumer_key)
start[i] = time.time()
place = api.geo_search(query="AU", granularity = "country")
place_id = place[0].id
screen_name = []
while True: 
    try:
        for tweet in tweepy.Cursor(api.search, q="place:%s"%place_id, until=datetime.datetime.today().strftime("%Y-%m-%d"),lang="en", tweet_mode="extended", max_id = maxid).items():
            #Cursoring the user screen name
            tweetJson = tweet._json
            maxid = str(tweet.id -1)
            if tweetJson['coordinates']:
                #coordinates to city
                longitude = tweetJson['coordinates']['coordinates'][0]
                latitude = tweetJson['coordinates']['coordinates'][1]
                ct = coor_to_city(longitude, latitude, tweetJson)
                if ct in cities:
                    if tweetJson['user']:
                        #if the screen name within the targeted place and ont recorded before, cursor the tweets by user_time_line
                        if tweetJson['user']['screen_name'] not in screen_name:
                            sn = tweetJson['user']['screen_name']
                            screen_name.append(sn)
                            for tweet in tweepy.Cursor(api.user_timeline, screen_name=sn, exclude_replies=False,lang="en", tweet_mode="extended").items():
                                tweetJson = tweet._json
                                get_tweets(tweetJson, dirty_word_dic)
                                tweecount += 1
                                print(tweecount)
                        
        
            elif tweetJson['place'] and tweetJson['place']['place_type'] == 'poi':
                #bounding box to city
                longitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][0] + tweetJson['place']['bounding_box']['coordinates'][0][2][0])/2
                latitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][1] + tweetJson['place']['bounding_box']['coordinates'][0][1][1])/2
                if longitude != 145.0531355 and latitude != -37.9725665:
                    ct = coor_to_city(longitude, latitude, tweetJson)
                    if ct in cities:
                        if tweetJson['user']:
                            #if the screen name within the targeted place and ont recorded before, cursor the tweets by user_time_line
                            if tweetJson['user']['screen_name'] not in screen_name:
                                sn = tweetJson['user']['screen_name']
                                screen_name.append(sn)
                                for tweet in tweepy.Cursor(api.user_timeline, screen_name=sn, exclude_replies=False,lang="en", tweet_mode="extended").items():
                                    tweetJson = tweet._json
                                    get_tweets(tweetJson, dirty_word_dic)
                                    tweecount += 1
                                    print(tweecount)


            elif tweetJson['place'] and tweetJson['place']['place_type'] == 'city':
                #city information stored by tweet
                ct = tweetJson['place']['name']
                if ct in cities:
                    if tweetJson['user']:
                        #if the screen name within the targeted place and ont recorded before, cursor the tweets by user_time_line
                        if tweetJson['user']['screen_name'] not in screen_name:
                            sn = tweetJson['user']['screen_name']
                            screen_name.append(sn)
                            for tweet in tweepy.Cursor(api.user_timeline, screen_name=sn, exclude_replies=False,lang="en", tweet_mode="extended").items():
                                    tweetJson = tweet._json
                                    get_tweets(tweetJson, dirty_word_dic)
                                    tweecount += 1
                                    print(tweecount)

    except tweepy.error.TweepError as e:
			# catch error
            print(e)
            print("#" + str(i + 1) + " changing to next credential due to the limit is reached")
            # change credentials
            if i == len(consumer_key) - 1:
                key = iter(consumer_key)
                secret = iter(consumer_secret)
                token = iter(access_token)
                a_secret = iter(access_secret)
                i = 0
            else:
                i += 1 
            # get new authentication
            auth = tweepy.OAuthHandler(next(key), next(secret))
            auth.set_access_token(next(token), next(a_secret))
            api = tweepy.API(auth)
            # verfiy the credential
            try:
                api.verify_credentials()
                print("verified credential")
            except:
                print("error in credential")

            if start[i] == None:
                start[i]  = time.time()
                print("changed to the" + str(i + 1) + " credential.")
                continue
            else:
                # check the waiting time, and do wait if necessary 
                sleeptime = (500) - round(time.time() - start[i])
                if sleeptime > 0:
                    time.sleep(sleeptime)
                start[i] = time.time()
                print("changed to the" + str(i + 1) + " credential.")
                continue
                        
