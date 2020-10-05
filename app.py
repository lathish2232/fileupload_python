from flask_restplus import reqparse, Api, Resource, fields
import os
import re
import math
import json
import operator
from collections import defaultdict, Counter
import csv
from datetime import datetime
from bs4 import BeautifulSoup

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS, cross_origin

import socket
import sys, threading, time

import yaml, requests

from datetime import timedelta

import sqlite3
import random
import requests
import time
import numpy as np

from datetime import datetime

import time
import copy

# Python program to create 
# a file explorer in Tkinter 

# import all components 
# from the tkinter library 
from tkinter import *

# import filedialog module 
from tkinter import filedialog 

import asyncio
loop = asyncio.get_event_loop()


app = Flask(__name__, static_url_path="/static/")
app.config["CORS_HEADERS"] = "Content-Type"
cors = CORS(app)

api = Api(app)
model_400 = api.model('ErrorResponse400', {
                      'message': fields.String,
'errors' :fields.Raw
})

model_500 = api.model('ErrorResponse400', {
'status': fields.Integer,
'message':fields.String
})

async def get_file(d):
       try:
           filename=None
           Tk().withdraw()
           filename=filedialog.askopenfilenames()
           print(filename)
           d["filename"]=filename
       except:
          print("Failure")
       finally:
          return filename

# file Data
@api.route('/file_upload' )
class fileupload(Resource):
  @api.response(200, 'Successful')
  @api.response(400, 'Validation Error', model_400)
  @api.response(500, 'Internal Processing Error', model_500)
  def get(self):
     """
     This function stores 
     """
     return_status = None
     payload_data = request.get_json()
     result = {}

     print(payload_data)
     try:
       d={"filename":None}
       res=loop.run_until_complete(get_file(d))
       result['status'] = 1
       result['message']=d
     except ValueError as e:
        result = {}
        print('Value Exception while submitting  Data')
        result['status'] = 0
        return_status = 400
        result['message'] = e.args[0]
     except :
        result = {}
        print('Exception while submitting trackermqtt Data')
        return_status = 500
        result['status'] = 0
        result['message'] = 'Internal Error has occurred while processing the Data'
     finally:
        resp = Response(json.dumps(result), status=return_status, mimetype="application/json")
     return resp

if __name__ =='__main__':
  port =  5000
  print(port)
  print("running ...")
  app.run()
