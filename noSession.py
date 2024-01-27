import requests
from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar
USER_NAME = "{user name}"#c000000000
PASSWORD="{password}"#password

#開発環境用。削除してください。
from account import USER_NAME,PASSWORD
print(USER_NAME,PASSWORD)


def request_log(func):
    def inner(*args,**kwargs):
        response= func(*args,**kwargs)
        print(f"redirect:{response.headers.get('Location')}")
        print(f"current url:{response.url}")
        print(f"cookies:{response.cookies}")
        print("\n")
        return response
    return inner

class MyRequests:
    def __init__(self) -> None:
        self.cookies = RequestsCookieJar()

    @request_log
    def get(self,url):
        response = requests.get(
            url=url,
            allow_redirects=False,
            cookies=self.cookies
        )
        if(self.cookies != None):
            self.cookies.update(response.cookies)
        else:
            self.cookies = response.cookies
        return response
    
    @request_log
    def post(self,url,data):
        response = requests.post(
            url=url,
            allow_redirects=False,
            cookies=self.cookies,
            data=data
        )
        if(self.cookies != None):
            self.cookies.update(response.cookies)
        else:
            self.cookies = response.cookies
        return response


#cookieを取得するため、リダイレクトを許可せず全てのページにアクセス
#cookieはMyRequestsが保持
req = MyRequests()

#ログインページの基底サイトにアクセス。
response_1_1 = req.get("https://eweb.stud.tokushima-u.ac.jp/Portal/shibboleth_login.aspx")

response_1_2 = req.get(response_1_1.headers["Location"])

response_1_3 = req.get("https://localidp.ait230.tokushima-u.ac.jp"+response_1_2.headers["Location"])

with open('output1.html', 'w', encoding='utf-8') as file:
    file.write(response_1_3.text) 



#ログイン処理
response_2 = req.post(
        url=response_1_3.url,
        data={
            "j_username": USER_NAME,
            "j_password": PASSWORD,
            "_eventId_proceed":""
        }
    )
#このページで認証情報が生成されるっぽい
with open('output2.html', 'w', encoding='utf-8') as file:
    file.write(response_2.text) 

#HTMLファイルを解析し、認証情報を取り出す
res2_soup = BeautifulSoup(response_2.content,"html.parser")
info = res2_soup.findAll("input")
RelayState = info[0]["value"]
SAMLResponse=info[1]["value"]



#認証情報をもとに、教務システムにログインする
response_3_1 = req.post(
    url = "https://eweb.stud.tokushima-u.ac.jp/Shibboleth.sso/SAML2/POST",
    data={
        "RelayState":RelayState,
        "SAMLResponse":SAMLResponse
        }
    )
response_3_2 = req.get(response_3_1.headers["Location"])

with open('output3.html', 'w', encoding='utf-8') as file:
    file.write(response_3_1.text) 



#ログイン完了したので、自由にスクレイピング可能。今回は時間割を開いてみた
response_4 = req.get("https://eweb.stud.tokushima-u.ac.jp/Portal/StudentApp/Regist/RegistList.aspx")

with open('output4.html', 'w', encoding='utf-8') as file:
    file.write(response_4.text) 


#時間割の部分だけ抽出
res4_soup = BeautifulSoup(response_4.content,"html.parser")
table_lecture = res4_soup.find(id="tblLecture")
table_others = res4_soup.find(id="tblOhters")
with open('table.html', 'w', encoding='utf-8') as file:
    file.write(str(table_lecture)+str(table_others)) 

