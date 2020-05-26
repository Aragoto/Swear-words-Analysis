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


def get_n_process(tweet, dirty_word_dic):
    tweetJson = tweet._json
    dataDict = {}
    dirty_word_dic = GetDirtyList()
    print(tweetJson)
    if tweetJson.get('user'):
        dataDict['id'] = tweetJson['id']
    if tweetJson.get('full_text'):
        text = tweetJson['full_text']
        dataDict['text'] = text
        blob = TextBlob(text)
        dataDict['polarity'] = blob.sentiment.polarity
        if tweetJson['coordinates']:
            longitude = tweetJson['coordinates']['coordinates'][0]
            latitude = tweetJson['coordinates']['coordinates'][1]
            ct = coor_to_city(longitude, latitude, tweetJson)
            if ct in cities:
                dataDict['geo'] = tweetJson['place']['name']
                    
        elif tweetJson['place'] and tweetJson['place']['place_type'] == 'poi':
                longitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][0] + tweetJson['place']['bounding_box']['coordinates'][0][2][0])/2
                latitude = (tweetJson['place']['bounding_box']['coordinates'][0][0][1] + tweetJson['place']['bounding_box']['coordinates'][0][1][1])/2
                if longitude != 145.0531355 and latitude != -37.9725665:
                        ct = coor_to_city(longitude, latitude, tweetJson)
                        if ct in cities:
                            dataDict['geo'] = ct
        else:
            dataDict['geo'] = "not specified"
        CheckTweetID_And_AddToDB(dataDict, dirty_word_dic)



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

def DirtyWordProcess(dataDict, dirty_word_dic):
    dirty_word_dic = GetDirtyList()
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
                db_entry["id"] = tmp_dic["id"]
                db_entry["city"] = tmp_dic["geo"]
                added_list.append(word)
                db_dirty.save(db_entry)
            else:
                pass

def EmotionProcess(dataDict):
    tmp_dic = dataDict
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
        db_entry["id"] = tmp_dic["id"]
        db_entry["emotion"] = dic_tweet["emotion"]
        db_emotion.save(db_entry)

def CheckTweetID_And_AddToDB(dataDict, dirty_word_dic):
    tmp_dic = dataDict
    id = str(tmp_dic["id"])
    db_entry = {}
    record = None
    if tmp_dic["geo"] != "not specified" and tmp_dic["geo"] != None:
        for rec in db_id.view('tweet_id_record/tweet_id', key = id, stale = "false"):
            record = rec
        if record == None:
            db_entry["tweet_id"] = id
            db_id.save(db_entry)
            EmotionProcess(dataDict)
            DirtyWordProcess(dataDict, dirty_word_dic)
        else:
            print(id, ", this tweet's information has been added to the database!")

parser = argparse.ArgumentParser(description='tweetscumulates')
parser.add_argument('--filename', type=str, default="log.txt")
args = parser.parse_args()



file = open(args.filename, "w")

def argsnb():
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
    nodes = argsnb()

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
    with open('suburb-geo-lga-new.json') as suburb_file:
        suburb_list = js.load(suburb_file)
        for suburb in suburb_list:
            if suburb['polygon']:
                polygon = []
                for coor in suburb['polygon']:
                    polygon.append(tuple(coor))
                suburb['polygon'] = polygon
    print('preporcessed')

    today = datetime.date.today()
    def get_targetDate(today):
        targetDate = today - datetime.timedelta(days = 7)
        targetDate = targetDate.strftime('%Y-%m-%d')
        return targetDate
    
    def dojob(i, maxid = None):
        auth = tweepy.auth.OAuthHandler(credentials[i]["consumer_key"], credentials[i]["consumer_secret"])
        auth.set_access_token(credentials[i]["access_token"], credentials[i]["access_secret"])
        api = tweepy.API(auth, wait_on_rate_limit=True)
        place = api.geo_search(query="AU", granularity = "country")
        place_id = place[0].id
        tweets = tweepy.Cursor(api.search, q="place:%s"%place_id, since=get_targetDate(today), until=today, tweet_mode="extended", max_id = maxid).items()
        while True:
            try:
                for tweet in tweets:
                    get_n_process(tweet, dirty_word_dic)
                    maxid = tweet._json.get('id')
            except tweepy.RateLimitError:
                print('Hit Twitter API rate limit.')
                if i < 2:
                    i += 1
                    dojob(i, maxid = maxid)
                else:
                    for i in range(3, 0, -1):
                        print("Wait for {} mins.".format(i * 5))
                        time.sleep(3 * 60)
                    i = 0
                    dojob(i, maxid=maxid)
            except tweepy.TweepError:
                print('\nCaught TweepError exception' )
                if i < 2:
                    i += 1
                    dojob(i, maxid=maxid)
                else:
                    for i in range(3, 0, -1):
                        print("Wait for {} mins.".format(i * 5))
                        time.sleep(3 * 60)
                    i = 0
                    dojob(i, maxid=maxid)
                continue
            except StopIteration:
                pass
            break

    dojob(0)
