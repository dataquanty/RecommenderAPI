#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:48:22 2017

@author: dataquanty
"""

from getreco import GetReco


from flask import json

import requests


res = requests.get('http://localhost:5000/reco/pred/6041')

userjson = {"gender":"M","age":18,"occupation":15,"zipcode":12300}
res = requests.post('http://localhost:5000/reco/adduser',json=userjson)
res.json()


ratingjson = {"userId":6044,"itemId":2646,"rating":5}
res = requests.post('http://localhost:5000/reco/adddata',json=ratingjson)
res.json()

res = requests.get('http://localhost:5000/reco/pred/6044')
res.json()