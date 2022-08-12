from urllib import request
from dotenv import load_dotenv
import os
import replicate
import requests
import json
import io
import sys
import pandas as pd
from pandas import json_normalize
from flask import g
import datetime

load_dotenv()
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
API_KEY = os.getenv('API_KEY')

def create_art(trance_title):
  user = str(g.user['id'])
  dt_now = datetime.datetime.now()
  dt_now_fmt = dt_now.isoformat()
  model = replicate.models.get("borisdayma/dalle-mini")
  img_lists = model.predict(n_predictions=4,prompt=trance_title)

  img_list = []
  file_name_list = []
  
  for list_item in img_lists:
    img_list.append(list_item['image'])

  for i in img_list:
    img = i
    file_name = './static/image/' + user + '_' + dt_now_fmt + i[-12:]
    file_name_list.append(file_name)
    res = requests.get(img)
    images = res.content
    with open(file_name,'wb') as f:
      f.write(images)
      
  return file_name_list        

#DeepL_APIの処理(翻訳して返す)
def deepL(inputtext):
  sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")

  text =  inputtext
  source_lang = 'JA'
  target_lang = 'EN'

  # パラメータの指定
  params = {
              'auth_key' : API_KEY,
              'text' : text,
              'source_lang' : source_lang, # 翻訳対象の言語
              "target_lang": target_lang  # 翻訳後の言語
          }

  # リクエストを投げる
  request = requests.post("https://api-free.deepl.com/v2/translate", data=params) # URIは有償版, 無償版で異なるため要注意
  result = request.json()
  
  df = json_normalize(result['translations'])
  trance_text = df.at[0,'text']

  return trance_text