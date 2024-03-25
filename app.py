from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

#======python的函數庫==========
import tempfile, os
import datetime
import openai
import time
#======python的函數庫==========

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
# OPENAI API Key初始化設定
openai.api_key = os.getenv('OPENAI_API_KEY')


context = [ {'role':'system', 'content':"""
        你是履歷助理機器人，為王裕順自動回復履歷內的信息。
        你要首先問候對方。然後等待用戶回複要詢問的信息
        回覆的資訊以下面的履歷來回答。

        履歷：
        Hi I'm 王裕順.
        I had 7 years of experience as a software engineer.
        Most of my current work is developing backends.
        I am good at using Java, ActionScript, Flex, and Spring and MVC architecture.
        In the first two years in current company, I participated to update a tool that programmer use to develop. 
        The technologies I used in this process as below:
        Spring
        PureMVC
        Generic MVC Platform
        JavaEE
        FlexActionScript
        PostgresSQL
        H2DataBase
        Hibernate
        Git
        Jenkins
        HTML5
        Vue
        This tool effectively improved the overall development efficiency by 80% after the revision.

        I currently work on a bank branch system project in my company, has developed the common functions and account opening business programs.
        I am familiar with the business logic of the financial industry.
        In the current project, use Java, Spring, Git and the above-mentioned revised tool to develop, to solve program problems, and to communicate directly with customers to solve specifications problems.
"""}
]



def GPT_response(text):
    # 接收回應
    prompt = text
    context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context) 
    context.append({'role':'assistant', 'content':f"{response}"})
     
    return response


def get_completion_from_messages(messages):
    # 接收回應
    response = openai.chat.completions.create(
        model = 'gpt-3.5-turbo',
        messages=messages,
        temperature=1
    )
    
    print(response.choices[0].message.content)
    return response.choices[0].message.content



# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    GPT_answer = GPT_response(msg)
    print(GPT_answer)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))

@handler.add(PostbackEvent)
def handle_message(event):
    print(event.postback.data)


@handler.add(MemberJoinedEvent)
def welcome(event):
    uid = event.joined.members[0].user_id
    gid = event.source.group_id
    profile = line_bot_api.get_group_member_profile(gid, uid)
    name = profile.display_name
    message = TextSendMessage(text=f'{name}歡迎加入')
    line_bot_api.reply_message(event.reply_token, message)
        
        
import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
