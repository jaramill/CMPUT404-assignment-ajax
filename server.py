#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

# I have this class to decide what to give back to GET http://.../world. My idea here is to reduce traffic. If  there haven't been POSTs after the timer has expired, send a special json object so that index.html  doesn't redraw. -Pablo

import time

class Timer:
    def __init__(self, timeout):
        self.t0 = time.clock()
        self.timeout = timeout

    def reset(self):
        self.t0 = time.clock()

    def expired(self):
        if time.clock() - self.t0 > self.timeout:
            return True
        else:
            return False    

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: appication/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()

# starting a timer with an expiration time of 1/30 seconds -Pablo
myTimer = Timer(1/30)          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data != ''):
        return json.loads(request.data)
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    # return None
    return redirect ("http://127.0.0.1:5000/static/index.html", code=302)


@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    # return None
    # reset the timer -Pablo
    myTimer.reset()
    v = flask_post_json()
    myWorld.set(entity, v)
    e = myWorld.get(entity)
    return json.dumps( e )

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    # return None
    # if there have been no recent posts, send a special json object, if not send the world 
    if myTimer.expired():
        return json.dumps({"redraw":0})
    else:
        return json.dumps(myWorld.world())
   

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    # return None
    return json.dumps(myWorld.get(entity))

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    # return None
    return json.dumps(myWorld.world())

if __name__ == "__main__":
    app.run()
