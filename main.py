import requests
from bs4 import BeautifulSoup
USER_NAME = "{user name}"#c000000000
PASSWORD="{password}"#password

#開発環境用。削除してください。
from account import USER_NAME,PASSWORD
print(USER_NAME,PASSWORD)

#sessionを開始。簡単にcookieを引き継いだだけでは動かなかった。
session = requests.Session()

#ログインページの基底サイトにアクセス。
response_1 = session.get(
    url="https://eweb.stud.tokushima-u.ac.jp/Portal/shibboleth_login.aspx"
    )
#リダイレクトされ、普段見るログインページに遷移
print(f"redirect:{response_1.history}")
print(f"current url:{response_1.url}")
print(f"cookies:{response_1.cookies}")

#ログイン処理
response_2 = session.post(
        url=response_1.url,
        data={
            "j_username": USER_NAME,
            "j_password": PASSWORD,
            "_eventId_proceed":""
            
        }
    )
#このページで認証情報が生成されるっぽい
#認証情報生成後のリダイレクトはJSによって制御されている
#つまり、requestsモジュールでは自動的に行われない

print(f"cookies:{response_2.cookies}")

#HTMLファイルを解析し、認証情報を取り出す
res2_soup = BeautifulSoup(response_2.content,"html.parser")
info = res2_soup.findAll("input")
RelayState = info[0]["value"]
SAMLResponse=info[1]["value"]

#認証情報をもとに、教務システムにログインする
#（リダイレクトを能動的に行う）
response_3 = session.post(
    url = "https://eweb.stud.tokushima-u.ac.jp/Shibboleth.sso/SAML2/POST",
    data={
        "RelayState":RelayState,
        "SAMLResponse":SAMLResponse
        }
    )

print(f"cookies:{response_3.cookies}")

#ログイン完了したので、自由にスクレイピング可能。今回は時間割を開いてみた
response_4 = session.get("https://eweb.stud.tokushima-u.ac.jp/Portal/StudentApp/Regist/RegistList.aspx")

#時間割の部分だけ抽出
res4_soup = BeautifulSoup(response_4.content,"html.parser")
table = res4_soup.findAll("table")
with open('table.html', 'w', encoding='utf-8') as file:
    file.write(str(table[12])+str(table[14])) 

#各レスポンスの時点で表示されるHTMLを出力しておく。
#output2はファイルを開いたらJSによりリダイレクトされるので開けない。
#エディタで開いてみてみてください。
with open('output1.html', 'w', encoding='utf-8') as file:
    file.write(response_1.text) 
with open('output2.html', 'w', encoding='utf-8') as file:
    file.write(response_2.text) 
with open('output3.html', 'w', encoding='utf-8') as file:
    file.write(response_3.text) 
with open('output4.html', 'w', encoding='utf-8') as file:
    file.write(response_4.text) 