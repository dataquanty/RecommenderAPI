#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:02:27 2017

@author: dataquanty
"""

from getreco import GetReco

from flask import Flask, json, request, abort, make_response
import pandas as pd

app = Flask(__name__)


rec = GetReco()

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/reco/pred/<int:userid>', methods=['GET'])
def predictInterests(userid):
    ratings = rec.predictInterests(int(userid))
    if(ratings == ''):
        abort(404)
    else:
        return json.jsonify(json.loads(ratings))
    


@app.route('/reco/adduser', methods=['POST'])
def adduser():
    if not request.json:
        abort(400)
    
    gender = request.json['gender']
    age = request.json['age']
    occupation = request.json['occupation']
    zipcode = request.json['zipcode']
    userId = rec.addUser(gender,age,occupation,zipcode)
    if userId == 0:
        abort(400)
    else:
        newuser = {
            'userId': userId,
            'gender':gender,
            'age': age,
            'occupation': occupation,
            'zipcode':zipcode
        }
        
        return json.jsonify({'user': newuser}), 201


@app.route('/reco/adddata', methods=['POST'])
def adddata():
    if not request.json:
        abort(400)
    userId = request.json['userId']
    itemId = request.json['itemId']
    rating = request.json['rating']
    res = rec.addData(userId,itemId,rating)
    if res==0:
        abort(400)
    else:
        rated = {
            'userId': userId,
            'itemId': itemId,
            'rating': rating
        }
        
        return json.jsonify({'rated': rated}), 201


@app.errorhandler(404)
def not_found(error):
    return make_response(json.jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(json.jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    app.run(debug=True)

