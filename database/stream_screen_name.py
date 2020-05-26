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


cities = ["Ballarat", "Banyule", "Baw Baw", "Bayside", "Benalla", "Boroondara", "Brimbank", "Campaspe",
"Cardinia", "Casey", "Colac-Otway", "Corangamite", "Darebin", "East Gippsland", "Frankston", "Greater Shepparton",
"Hobsons Bay", "Kingston", "Knox", "Latrobe", "Loddon", "Macedon Ranges", "Manningham",
"Maribyrnong", "Maroondah", "Melbourne", "Melton", "Mildura", "Mitchell", "Moira", "Monash", "Moreland", "Mornington Peninsula",
"Mount Alexander", "Nillumbik", "Northern Grampians", "Port Phillip", "Pyrenees", "South Gippsland", "Southern Grampians",
"Stonnington", "Glen Eira", "Greater Bendigo", "Greater Dandenong", "Greater Geelong", "Glenelg", "Surf Coast", "Swan Hill",
"Wangaratta", "Warrnambool", "Wellington", "Whitehorse", "Wodonga", "Wyndham", "Yarra", "Yarra Ranges"]



def in_suburb(longitude, latitude, suburb):
    point = Point(longitude, latitude)
    polygon = Polygon(suburb['polygon'])
    return point.within(polygon)

def coor_to_suburb(longitude, latitude, row):
    geo = ""
    for suburb in suburb_list:
        if in_suburb(longitude, latitude, suburb):
            geo = suburb['suburb']
            break
    return geo

def coor_to_city(longitude, latitude, row):
    city = ""
    for suburb in suburb_list:
        if in_suburb(longitude, latitude, suburb):
            city = suburb['lga_name']
            break
    return city


def process_sn(sn):
    creds = [{"consumer_key": 'KkBDT4dOceWxhGHp74rXUfg94',
            "consumer_secret": '0ZHuXmYEO5KiJGajvoV6aNIXmxsm3BmTOEq9VydiCKntJX76E5',
            "access_token": '1250618520771035136-A6IthX5Ub82m3SPQbeA8ZpvBsJhh4G',
            "access_secret": 'CMk5eTGG2HwFM2fhU9fCD7blUJCNzguwSjlSh2qczwmqs'},
            {"consumer_key": 'GF4mJg2nSNTS5hEhEVFt4yxSD',
            "consumer_secret": 'z0LedWOMxHcsb9zHu1yKYMiVBs0j3TAbJ885qDiq31hnl90Kcf',
            "access_token": '1252056724560769024-NIPwBvsWYkDw0sPNKLBTor97s0KKZY',
            "access_secret": 'XB67xjZSarPiQIqJoS5D4OKGq3qVOHddh861ozVAWEzmg'}]
    i = 0
    try:
        auth = tweepy.auth.OAuthHandler(creds[i]["consumer_key"], creds[i]["consumer_secret"])
        auth.set_access_token(creds[i]["access_token"], creds[i]["access_secret"])
    except:
        if i < 2:
            try:
                i = i + 1
                auth = tweepy.auth.OAuthHandler(creds[i]["consumer_key"], creds[i]["consumer_secret"])
                auth.set_access_token(creds[i]["access_token"], creds[i]["access_secret"])
            except:
                print("no enough credentials")
        else:
            print("no enough credentials")
            
    api = tweepy.API(auth, wait_on_rate_limit=True)
    try:
        tw = []
        tweets = tweepy.Cursor(api.user_timeline, screen_name=sn, exclude_replies=False, tweet_mode="extended").items()
        for tweet in tweets:
            tw.append(tweet._json)
        return tw
    except tweepy.RateLimitError:
            print('Hit Twitter API rate limit.')
            for i in range(3, 0, -1):
                print("Wait for {} mins.".format(i * 5))
                time.sleep(5 * 60)
    except tweepy.TweepError:
        print('\nCaught TweepError exception' )
        time.sleep(30)
    except StopIteration:
        pass
    


def get_tweets(sn):
    while True:
        try:
            tweets = process_sn(sn)
            for t in range(len(tweets)):
                dataDict = {}
                tweetJson = tweets[t]
                if tweetJson.get('full_text'):
                    text = tweetJson['full_text']
                    dataDict['text'] = text
                    blob = TextBlob(text)
                    dataDict['polarity'] = blob.sentiment.polarity
                    dataDict['id'] = tweetJson['id']
                    if tweetJson['coordinates']:
                        longitude = tweetJson['coordinates']['coordinates'][0]
                        latitude = tweetJson['coordinates']['coordinates'][1]
                        ct = coor_to_city(longitude, latitude, tweetJson)
                        if ct in cities:
                            dataDict['geo'] = tweetJson['place']['name']
                    elif tweetJson['place'] and tweetJson['place']['place_type'] == 'neighborhood':
                        ctw = tweetJson['place']['name']
                        if cs[ctw] in cities:
                            dataDict['geo'] = cs[ctw]
                    elif tweetJson['place'] and tweetJson['place']['place_type'] == 'poi':
                        longitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][0] + tweetJson['place']['bounding_box']['coordinates'][0][2][0])/2
                        latitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][1] + tweetJson['place']['bounding_box']['coordinates'][0][1][1])/2
                        if longitude != 145.0531355 and latitude != -37.9725665:
                                ct = coor_to_city(longitude, latitude, tweetJson)
                                if ct in cities:
                                    dataDict['geo'] = ct
                    else:
                        dataDict['geo'] = "not specified"

                    DirtyWordProcess(dataDict,dirty_word_dic)
                    EmotionProcess(dataDict)
    
                
            #return dataDict
        except:
            continue
                


def dealStream(tweetJson, file):
    try:
        screen_name = []
        if tweetJson['coordinates']:
            longitude = tweetJson['coordinates']['coordinates'][0]
            latitude = tweetJson['coordinates']['coordinates'][1]
            ct = coor_to_city(longitude, latitude, tweetJson)
            if ct in cities:
                if tweetJson.get('user'):
                    if tweetJson['user']['screen_name'] not in screen_name:
                        sn = tweetJson['user']['screen_name']
                        get_tweets(sn)
                        screen_name.append(sn)
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'neighborhood':
            ctw = tweetJson['place']['name']
            if cs[ctw] in cities:
                if tweetJson.get('user'):
                    if tweetJson['user']['screen_name'] not in screen_name:
                        sn = tweetJson['user']['screen_name']
                        get_tweets(sn)
                        screen_name.append(sn)
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'poi':
            longitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][0] + tweetJson['place']['bounding_box']['coordinates'][0][2][0])/2
            latitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][1] + tweetJson['place']['bounding_box']['coordinates'][0][1][1])/2
            if longitude != 145.0531355 and latitude != -37.9725665:
                ct = coor_to_city(longitude, latitude, tweetJson)
                if ct in cities:
                    if tweetJson.get('user'):
                        if tweetJson['user']['screen_name'] not in screen_name:
                            sn = tweetJson['user']['screen_name']
                            get_tweets(sn)
                            screen_name.append(sn)
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'city':
            ct = tweetJson['place']['name']
            if ct in cities:
                if tweetJson.get('user'):
                    if tweetJson['user']['screen_name'] not in screen_name:
                        sn = tweetJson['user']['screen_name']
                        get_tweets(sn)
                        screen_name.append(sn)
        return screen_name
    

    except Exception as e:

        print(e)
        file.write(str(e) + "\n")
        time.sleep(30)


def GetDirtyList():
    
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

def DirtyWordProcess(posttweet, dirty_word_dic):
    tmp_dic = posttweet
    if tmp_dic["geo"] != None and tmp_dic["geo"] != "not specified" and  tmp_dic["geo"] != "" and tmp_dic["geo"] != None:
        txt = tmp_dic["text"]
        txt = txt.lower() #将tweet单词变为小写
        tmp_list = re.findall(r"\w+",txt)#将tweet变为单词list
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

def EmotionProcess(posttweet):
    tmp_dic = posttweet
    if tmp_dic["geo"] != None and tmp_dic["geo"] != "not specified" and  tmp_dic["geo"] != "" and tmp_dic["geo"] != None:
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




parser = argparse.ArgumentParser(description='screen_names')
parser.add_argument('--filename', type=str, default="log.txt")
args = parser.parse_args()



file = open(args.filename, "w")

class TweetListener(StreamListener):

    def on_data(self, data):

        tweetJson = js.loads(data, encoding= 'utf-8')
        if not tweetJson["text"].startswith('RT') and tweetJson["retweeted"] == False:
            file.write(data)
            dealStream(tweetJson, file)
        return True

    def on_error(self, status):
        print (status)

def args():
    FLAG = argparse.ArgumentParser(description='servers')
    FLAG.add_argument('--nginx')
    FLAG.add_argument('--backup1')
    FLAG.add_argument('--backup2')
    arguments = FLAG.parse_args()
    return arguments


if __name__ == '__main__':
    credentials = [
            {"consumer_key": '6ETA0Zjw2bS7htWkcwYsmY4kA',
            "consumer_secret": 'chJp4AxFAhikIWXnJ2wIq4zqaXtygARIKcbyNJa67PH7NwDiww',
            "access_token": '1251842554141618176-BCDBIcPK3Zx5SpyOrMGS01N4vk2dEg',
            "access_secret": 'aGru0K5H08XE3Ddr4S2od84eFXKdtxNQwBn4rI3AVcevc'},
            {"consumer_key": 'mLE5EPHyhF5V19V0SLALg75Kj',
            "consumer_secret": 'X4PiePNaxqEiNcneh1XxPyoEQ9oMbWG3dZEk7EYgdPm8vKf2UE',
            "access_token": '3401543464-JvCeSmLjLZFGwSKWZDDwcFH7RJLULbrVhoR0uCz',
            "access_secret": '7xqyLryUNWSNylEavarSCsYiiLHFzV8BwaWekgTMJImfY'},
            {"consumer_key": 'K4YJd9q5ylUZK2wNMJMPM4xW3',
            "consumer_secret": '0WkiJzyQoDckShkIehCOQaji5hSECQMiV81dTICaJLnld3hOC7',
            "access_token": '1251863760513318917-J9sAJ89k4quQ78VQ5kTNG2AQIgn0wG',
            "access_secret": 'wvMWdR72wcWUFrRbdi3f1gMAi2Ul4qqTJ3sZ7XdiY90EI'}]
    nodes = args()

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
    cs = {}
    dirty_word_dic = GetDirtyList()
    with open('suburb-geo-lga-new.json') as suburb_file:
        suburb_list = js.load(suburb_file)
        for suburb in suburb_list:
            if suburb['polygon']:
                polygon = []
                for coor in suburb['polygon']:
                    polygon.append(tuple(coor))
                suburb['polygon'] = polygon
            if suburb['lga_name'] in cities:
                cs[suburb['suburb']] = suburb['lga_name']
    print('preporcessed')
    

    def dojob(i):
        start_time = time.time()
        listener = TweetListener()
        try:
            auth = tweepy.OAuthHandler(credentials[i]["consumer_key"], credentials[i]["consumer_secret"])
            auth.set_access_token(credentials[i]["access_token"], credentials[i]["access_secret"])
            while True:
                try:
                    stream = Stream(auth, listener)
                    stream.filter(languages=["en"], locations = [140.961682, -39.15919, 149.976679, -33.980426])
                except:
                    continue
            end_time = time.time()
            tot = end_time - start_time
            if tot > 7200:
                i = i + 1
                if i < 2:
                    dojob(i)
        except:
            i = i + 1
            if i < 2:
                dojob(i)

    
    dojob(0)
    #process_sn("realDonaldTrump")
    file.close()
