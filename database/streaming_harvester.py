import tweepy
from tweepy.streaming import StreamListener

from tweepy import OAuthHandler
from tweepy import Stream
import json as js
import argparse
from datetime import datetime
import couchdb
from textblob import TextBlob
from shapely.geometry import Point, Polygon
import time
import re
import argparse
import socket
import http.client
import urllib3

from http.client import IncompleteRead as http_incompleteRead
from urllib3.exceptions import IncompleteRead as urllib3_incompleteRead


cities = ["Ballarat", "Banyule", "Baw Baw", "Bayside", "Benalla", "Boroondara", "Brimbank", "Campaspe",
"Cardinia", "Casey", "Colac-Otway", "Corangamite", "Darebin", "East Gippsland", "Frankston", "Greater Shepparton",
"Hobsons Bay", "Kingston", "Knox", "Latrobe", "Loddon", "Macedon Ranges", "Manningham",
"Maribyrnong", "Maroondah", "Melbourne", "Melton", "Mildura", "Mitchell", "Moira", "Monash", "Moreland", "Mornington Peninsula",
"Mount Alexander", "Nillumbik", "Northern Grampians", "Port Phillip", "Pyrenees", "South Gippsland", "Southern Grampians",
"Stonnington", "Glen Eira", "Greater Bendigo", "Greater Dandenong", "Greater Geelong", "Glenelg", "Surf Coast", "Swan Hill",
"Wangaratta", "Warrnambool", "Wellington", "Whitehorse", "Wodonga", "Wyndham", "Yarra", "Yarra Ranges"]

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



def dealStream(tweetJson):
    #get the qualified tweet and process it to normalized data
    try:
        print(tweetJson)
        dataDict = {}
        dataDict["text"] = tweetJson["text"]
        text = tweetJson['text']
        blob = TextBlob(text)
        dataDict["polarity"] = blob.sentiment.polarity
        dataDict["geo"] = None
        #generate the sentiment of the text
        if tweetJson.get('user'):
            dataDict['id'] = tweetJson['id']
        if tweetJson['coordinates']:
            #coordinates to city
            longitude = tweetJson['coordinates']['coordinates'][0]
            latitude = tweetJson['coordinates']['coordinates'][1]
            ct = coor_to_city(longitude, latitude, tweetJson)
            if ct in cities:
                dataDict["geo"] = ct
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'poi':
            #bounding box to city
            longitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][0] + tweetJson['place']['bounding_box']['coordinates'][0][2][0])/2
            latitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][1] + tweetJson['place']['bounding_box']['coordinates'][0][1][1])/2
            if longitude != 145.0531355 and latitude != -37.9725665:
                ct = coor_to_city(longitude, latitude, tweetJson)
                if ct in cities:
                    dataDict["geo"] = ct
            else:
                dataDict["geo"] = "not specified"
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'city':
            #city information stored by tweet
            ct = tweetJson['place']['name']
            if ct in cities:
                dataDict["geo"] = ct
        else:
            dataDict["geo"] = "not specified"
        CheckTweetID_And_AddToDB(dataDict)
    

    except Exception as e:
        #sleep the system for 30 sec to handling exception
        print(e)
        print("what")
        time.sleep(30)




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



parser = argparse.ArgumentParser(description='Streaming_harvester')
#parser.add_argument('--filename', type=str, default="logstream.txt")
args = parser.parse_args()



#file = open(args.filename, "w")

class TweetListener(StreamListener):

    def on_data(self, data):
        try:
            tweetJson = js.loads(data, encoding= 'utf-8')
            if not tweetJson["text"].startswith('RT') and tweetJson["retweeted"] == False:
                #file.write(data)
                dealStream(tweetJson)

            return True

        except BaseException as e:
            print(e)
            time.sleep(10)
            return True

        except http_incompleteRead as e:
            print(e)
            time.sleep(10)
            return True
        except urllib3_incompleteRead as e:
            print(e)
            time.sleep(10)
            return True
        

    def on_error(self, status_code):
        #Handle other errors
        print (status_code)
        if status_code == 420:
            time.sleep(10)
        if status_code == 429:
            time.sleep(15*60 + 1)
        else:
            time.sleep(10)
        return True

    def on_timeout(self):
        print("Timeout")
        return True




if __name__ == '__main__':
    

    
    couch = couchdb.Server('http://admin:password@localhost:5984')
    

    db_dirty = couch["dirty_words"]
    db_emotion = couch["emotion"]
    db_id = couch["tweet_id"]
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

    listener = TweetListener()
    #get the authentication to deploy api
    auth = tweepy.OAuthHandler('QaTGPoZHlRLZ89yNxNIFSB8SX', 'HwUzHPeCwDks7l0pb5jzReMBp7GcpLMmY266z3T0aWqq0ILMhm')
    auth.set_access_token('1251842554141618176-nJRFuGIxRWVTPoGBudpOTIanAarEag', 'Vlymkbhc3XC7IZ7V1A80EnigR8D3olqzHrwA70Rbq8HbV')
    
    #stream the tweets with constraints language to be English, and location within the cities around Melbroune
    while True:
        try:
            stream = Stream(auth, listener)
            stream.filter(languages=["en"], locations = [140.961682, -39.15919, 149.976679, -33.980426])
        except Exception as e:
            print('Exception:', e)
        pass
