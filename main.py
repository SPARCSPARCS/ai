from typing import Union
from fastapi import FastAPI, UploadFile
from bs4 import BeautifulSoup
import requests
import urllib.parse
from pydantic import BaseModel
import re
import uuid
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from urllib import parse
import json
import requests



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


class getContent(BaseModel):
    content: str

app = FastAPI()
app.mount("/files", StaticFiles(directory="files"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def read_url(url: str):

    content = get_url(url)
    return {"content": content }


@app.post("/upload/")
async def create_upload_file(file: UploadFile):
    get_uuid = uuid.uuid4()
    file_array = file.filename.split(".")
    file_location = f"files/{get_uuid}.{file_array[len(file_array)-1]}"

    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    return {"filename": file_location}


@app.get("/stt/")
async def create_upload_file(url: str):
    client_id = "owkwud0ncz"
    client_secret = "vzbBnTJpXNDvQ5ZJfTEBCEFNYCAjimSwfkKCnKyL"
    lang = "Kor"
    req_url = "https://naveropenapi.apigw.ntruss.com/recog/v1/stt?lang=" + lang
    data = open("./"+url, 'rb')

    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/octet-stream"
    }
    response = requests.post(req_url,  data=data, headers=headers)
    rescode = response.status_code
    if(rescode == 200):
        print (response.json())
        result = response.json()
        return {"response": result["text"]}
    else:
        print("Error : " + response.text)



@app.get("/news/")
def get_news(query: str):
    req_url = "https://openapi.naver.com/v1/search/news.json?query={0}&sort=sim".format(query)

    headers = {
        "X-Naver-Client-Id": "4X7DdLAk2Xw6_04BvJI5",
        "X-Naver-Client-Secret": "4qTdoDCMM6",
    }

    response = requests.get(req_url, headers=headers)
    rescode = response.status_code
    if(rescode == 200):
        print (response.json())
        result = response.json()
        return {"response": result["items"]}
    else:
        print("Error : " + response.text)



@app.post("/questions")
def get_sample_array(req: getContent):
    input_content = parse.unquote(req.content)
    
    preset_text = [
        {
            "role":"system",
            "content":"너는 채용담당자야. 사용자가 채용 공고 링크를 보내면 그에 맞는 면접 질문을 배열 형태로 출력하는 역할이야. 한국어로 답변하고 엄격한 언어로 길게 답변해. 그리고 각 질문마다 \"||\" 를 구분자로 사용해."
        },
        {
            "role":"user",
            "content":"{0} 해당 채용 공고를 분석해서 채용공고의 예상 면접 질문을 5개 생성하고 각 질문마다 \"||\" 를 구분자로 사용해. 질문은 총 5개고 추가적인 설명이나 타이틀 또는 번호 없이 면접 질문만 출력해".format(input_content)
        }
    ]

    request_data = {
        'messages': preset_text,
        'topP': 0.8,
        'topK': 0,
        'maxTokens': 256,
        'temperature': 0.5,
        'repeatPenalty': 5.0,
        'stopBefore': [],
        'includeAiFilters': True,
        'seed': 0
    }

    headers = {
        'X-NCP-CLOVASTUDIO-API-KEY': 'NTA0MjU2MWZlZTcxNDJiY71zbl8q71f1sERnVRwzt+RZzWbe5i+VpjnKxSOpoXuV',
        'X-NCP-APIGW-API-KEY': 'UDVKcQUFxEzQ5JnZdVZfrGw9pIcljFyiWz7y9rKg',
        'X-NCP-CLOVASTUDIO-REQUEST-ID': '88ffa858-ad67-4e88-80c2-bc9df748de28',
        'Content-Type': 'application/json; charset=utf-8',
    }


    response = requests.post('https://clovastudio.stream.ntruss.com/testapp/v1/chat-completions/HCX-003', headers=headers, json=request_data, stream=False)
    result = response.json()

    return {"result": result["result"]["message"]["content"].split("||") }
