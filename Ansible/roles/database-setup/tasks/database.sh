#!/bin/bash
echo "== create database =="
curl -X PUT http://admin:password@localhost:5984/dirty_words
curl -X PUT http://admin:password@localhost:5984/emotion
curl -X PUT http://admin:password@localhost:5984/tweet_id
python3 /home/ubuntu/database/make_dirty_view_2.py
python3 /home/ubuntu/database/make_emotion_view_2.py
python3 /home/ubuntu/database/make_tweet_id_view.py

