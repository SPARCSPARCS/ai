from typing import Union
from fastapi import FastAPI, UploadFile
from bs4 import BeautifulSoup
import requests
import urllib.parse
from pydantic import BaseModel
import re
import uuid
from fastapi.staticfiles import StaticFiles

# import scrapy
# from scrapy import Spider
# from scrapy.crawler import CrawlerProcess


# class UrlSpider(Spider):
#     name = "url"

#     def start_requests(self):
#         yield scrapy.Request(global_url, self.parse_start)

#     def parse_start(self, response):
#         print(response.body)
#         return response.body

class getUrl(BaseModel):
    url: str


app = FastAPI()
app.mount("/files", StaticFiles(directory="files"), name="static")

def get_url(url):
    get_url_data = requests.get(url)
    html_data = BeautifulSoup(get_url_data.text, 'html.parser') 
    find_tag = html_data.find_all(['p', 'h1', 'h2', 'h3'])
    data = ""

    for i in range(len(find_tag)):
        print(f"{i}. {find_tag[i].text}")
        data += find_tag[i].text

    if data == "": # NOTE: SSR 아닐시 불가능 예: https://careers.kakao.com/jobs/P-13720?skillSet=&part=TECHNOLOGY&company=KAKAO&keyword=&employeeType=&page=1
        print("")

    return data


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/test/url")
def read_url(req: getUrl):

    content = get_url(req.url)
    return {"content": content }


@app.post("/upload/")
async def create_upload_file(file: UploadFile):
    get_uuid = uuid.uuid4()
    file_array = file.filename.split(".")
    file_location = f"files/{get_uuid}.{file_array[len(file_array)-1]}"

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return {"filename": file_location}