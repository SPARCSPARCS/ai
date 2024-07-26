from typing import Union
from fastapi import FastAPI
from bs4 import BeautifulSoup
import requests
import urllib.parse
from pydantic import BaseModel
import re

class getUrl(BaseModel):
    url: str


app = FastAPI()

def get_url(url):
    get_url_data = requests.get(url)
    html_data = BeautifulSoup(get_url_data.text, 'html.parser') 
    find_tag = html_data.find_all(['p', 'h1', 'h2', 'h3'])
    data = ""

    for i in range(len(find_tag)):
        print(f"{i}. {find_tag[i].text}")
        data += find_tag[i].text

    return data


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test/url")
def read_url(req: getUrl):
    content = get_url(req.url)
    return {"content": content }

