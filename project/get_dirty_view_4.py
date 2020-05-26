import couchdb
import argparse
import socket

from get_nodes import get_ip

# nodes IPs
nginx = get_ip('nginx')
master = get_ip('master')
slave1 = get_ip('slave1')
slave2 = get_ip('slave2')

nodes = {'master-node': master, 'slave-node1': slave1, 'slave-node2': slave2}
hostname = socket.gethostname()
hostname = hostname.lower()
del nodes[hostname]
backup1 = list(nodes.values())[0]
backup2 = list(nodes.values())[1]

# try different serverses in case of lost connection
# Connect to couchDB emotion database
try:
    couch = couchdb.Server('http://admin:password@localhost:5984')
    db = couch["dirty_words"]
except:
    try:
        couch = couchdb.Server('http://admin:password@' + nginx + ':5984')
        db = couch["dirty_words"]
    except:
        try:
            couch = couchdb.Server('http://admin:password@' + backup1 + ':5984')
            db = couch["dirty_words"]
        except:
            try:
                couch = couchdb.Server('http://admin:password@' + backup2 + ':5984')
                db = couch["dirty_words"]
            except Exception as e:
                print("Can not access to the database! \n Please Check your internet.")



def get_dirty():
    item_dirty = []

    # iterate the doc in the view, to get swear words in tweets and where this tweet posted
    # since we only have one key, we use group = True
    # stale = "update_after" means stable = true, update = false
    for item in db.view('dirty_words/dirty_geo', group=True, stale="update_after"):
        dic = {"city": item["key"], "dirty_word_count": item["value"]}
        item_dirty.append(dic)

    return item_dirty
