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

import copy

signature_template={'parameter_name':None,
                    'parameter_data_type':None,
                    'is_required':None,
                    'parameter_default_value':None,
                    'user_value':None,
                    'help':None}

class Method_Signature():
    def __init__(self,method):
        self.method=method
        self.argspec=inspect.getfullargspec(self.method)
        self.signature=[]
    def get_optional_params(self):
        defaults={}
        if self.argspec.defaults is not None:
           defaults=dict(zip(self.argspec.args[-len(self.argspec.defaults):],self.argspec.defaults))
        if self.argspec.kwonlydefaults is not None:
           defaults.update(self.argspec.kwonlydefaults)
        return defaults

    def get_param_datatype_help_content(self,param_name):
        dtypes={'int':"Integer","str":"String","float":"Float","list":"List","dict":"Dictionary","set":"Set","bool":"Boolean"}
        data_type=None
        content=[]
        param_help=self.method.__doc__.split("\n")
        for index,line in enumerate(param_help):
            if param_name in line and ":" in line:
                dtype_info=line.split(":")[1]
                for dtype in dtypes:
                    if dtype in dtype_info:
                        data_type=dtypes[dtype]
                        break
                if not data_type:
                    data_type=dtype_info
                for help_content in  param_help[index+1:]:
                    if not ":" in help_content:
                         content.append(help_content)
                    break
                break
        help_str=None
        if content:
           help_str="\n".join(content)
        return (data_type,help_str)

    def get_signature(self):
        total_params=self.argspec.args
        optional_params=self.get_optional_params()
        for param_name in total_params:
            signature_params=copy.deepcopy(signature_template)
            signature_params["parameter_name"]=param_name
            parameter_data_type,help_content=self.get_param_datatype_help_content(param_name)
            signature_params["parameter_data_type"]=parameter_data_type
            signature_params["help"]=help_content
            signature_params["is_required"]=True
            if param_name in optional_params:
               signature_params["is_required"]=False
               signature_params["parameter_default_value"]=optional_params[param_name]
            self.signature.append(signature_params)
        return self.signature

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
      window =Tk()
      window.withdraw()
      filename=filedialog.askopenfilenames()
      filename=filename[0]
      window.attributes('-topmost', True)
      window.destroy()
      d["filename"]=filename
      d["filetype"] =os.path.splitext(filename)[1][1:]
      method=pd.read_csv
      meta_data_obj=Method_Signature(method)
      d["function"] =pd.read_csv.__name__
      d["signature"]=meta_data_obj.get_signature()
      del meta_data_obj  
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
   print("running ...")
   app.run()
