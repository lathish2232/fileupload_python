from flask_restplus import reqparse, Api, Resource, fields
import os

import json

import csv
from datetime import datetime
from bs4 import BeautifulSoup

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS, cross_origin


from datetime import timedelta
import inspect
import pandas as pd

from tkinter import *
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
      filename=filename[0]
      d["filename"]=filename
      d["filetype"] =os.path.splitext(filename)[1][1:]
      d["function"] =pd.read_csv.__name__
      d["signature"] =str(inspect.signature(pd.read_csv))
           
   except:
      print("Failure")
   finally:
      return filename

def file_metadata_process (filename,filetype):
   if filetype == "csv":
      DF=pd.read_csv(filename,nrows=1).head(1)
   else:
      DF=pd.read_excel(filename,nrows=1).head(1)
   res={}
   for k,v in DF.dtypes.to_dict().items():
      if str(v)=="object":
         v="string"
      res[k]=str(v)
   return res
        
def sample_data(filename,filetype):
   if filetype == "csv" :
      data= json.loads(pd.read_csv(filename).to_json (orient="records"))
   else:
      data=json.loads(pd.read_excel(filename).to_json (orient="records"))
   return data
         

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
       d={"filename":None,"filetype":None,"function":None,"signature":None}
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

@api.route('/file_data' )
class fileupload(Resource):
   @api.response(200, 'Successful')
   @api.response(400, 'Validation Error', model_400)
   @api.response(500, 'Internal Processing Error', model_500)
   def post(self):
      """
      This function stores 
      """
      return_status = None
      payload_data = request.get_json()
      result = {}

      print(payload_data)
      try:
         d={"file_metadata":None,"file_data":None}
        
         d["file_metadata"]=file_metadata_process(payload_data['filename'],payload_data['filetype'])
         d["file_data"] =sample_data(payload_data['filename'],payload_data['filetype'])
         result['status'] = 1
         result['message']=d
      except ValueError as e:
         result = {}
         print('Value Exception while submitting  Data')
         result['status'] = 0
         return_status = 400
         result['message'] = e.args[0]
      except Exception as e:
         result = {}
         print('Exception while submitting  Data')
         return_status = 500
         result['status'] = 0
         result['message'] = 'Internal Error has occurred while processing the Data %s'%str(e)
      finally:
         resp = Response(json.dumps(result), status=return_status, mimetype="application/json")
      return resp

if __name__ =='__main__':
   port =  5000
   print(port)
   print("running ...")
   app.run()
