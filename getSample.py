import requests
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import os
import shutil

def parseArgs():
    parser = argparse.ArgumentParser()
    #コンテストのURL
    parser.add_argument("url", help="https://atcoder.jp/contests/abc156")
    args = parser.parse_args()

    return args

# 親ディレクトリを作成する関数
def createParentPath(filepath):
    head, _ = os.path.split(filepath)
    if len(head) != 0:
        os.makedirs(head, exist_ok = True)


def login(LOGIN_URL="https://atcoder.jp/login"):
    # セッション開始
    session = requests.session()

    # csrf_token取得
    r = session.get(LOGIN_URL)
    s = BeautifulSoup(r.text, 'lxml')
    csrf_token = s.find(attrs={'name': 'csrf_token'}).get('value')

# パラメータセット
    login_info = {
        "csrf_token": csrf_token,
        "username": "Your username",
        "password": "Your password"
    }

    # LOGIN_URLにlogin_infoの情報をポストしてログインを試みる。     
    result = session.post(LOGIN_URL, data=login_info)
    result.raise_for_status()
    # ログインできたかどうかまで判断要素としていため、正確にusernameとpasswordを書き込む。  
    if result.status_code==200:
        # LOGIN_URLに問題なく送信することができた時  
        print("Log in!")
    else:
        print("failed...")

    return session

def getSample(session, url):
    problems = {}
    """
    problem[Q] = url
    問題Qへのurl
    """
    sample = {}
    """
    sample[Q] = sam
    問題Qのサンプル群
    sam = [入力サンプル1、入力サンプル1の答え、入力サンプル2、...]
    """
     
    lang = "?lang=en"
    r = session.get(url)#対象コンテストのURLのhtmlを入手

    # 絞り込み開始
    soup = BeautifulSoup(r.content, "lxml")
    # コンテストサイトのナビバー部分を探す
    soup = soup.find(id="contest-nav-tabs")
    #ナビバーのaタグを探し出し、そのうちTasksを指すものからurl(url先は問題一覧のページ）を取り出す。
    soup = soup.find_all("a")
    for s in soup:
        if s.text == " Tasks":
            url = s.attrs["href"]

    #問題ページのURLを作成、html取得
    url = urljoin(args.url, url)
    url += lang
    r = session.get(url)
    soup = BeautifulSoup(r.content, "lxml")
    soup = soup.find_all(class_="text-center no-break")
    # 各問題に遷移するためのurl取得
    for s in soup:
        s = s.find("a")
        url= s.attrs["href"]
        url = urljoin(args.url, url)
        url += lang
        problems[s.string] = url 

    # 各問題が書かれているページの中からサンプルを取得
    for s, url in problems.items():
        r = session.get(url)
        soup = BeautifulSoup(r.content, "lxml")
        soup = soup.find("span", class_="lang-ja")
        ex = soup.find(class_="io-style").find("pre")

        soup = soup.find_all("pre")
        sam = []
        for so in soup:
            if so == ex:
                continue
            elif so.string is None:
                continue
            sam.append(so.string)
        #sam = sorted(set(sam), key=sam.index)
        sample[s] = sam
   
    return sample

def writeSamplesToFile(samples, directory):
    # 取得したサンプルをテキストファイルに書き込み、保存
    for Q, tasks in samples.items():
        cnt = 0
        count = 0
        task_q = []
        task_ans = []
        #このコードを実行しているディレクトリ内にコンテスト名のディレクトリを作成
        os.makedirs(directory + "/" + Q, exist_ok=True)
        shutil.copy("shortcuts/testSamples.sh", directory + "/" + Q)
        shutil.copy("shortcuts/submit.py", directory + "/" + Q)
        
        for task in tasks:
            # 問題を保存
            if cnt % 2 == 0:
                count += 1
                
                sepFilePath = directory + "/" + Q + "/task_" + str(count) + ".txt"
                task_q.append(task)
                with open(sepFilePath, mode="w") as f:
                    task = task.replace("\r\n", "\n")
                    f.writelines(task)

            #答えを保存
            else:
                sepFilePath = directory + "/" + Q + "/ans_" + str(count) + ".txt"
                
                task_ans.append(task)
                with open(sepFilePath, mode="w") as f:
                    task = task.replace("\r\n", "\n")

                    f.writelines(task)

            cnt += 1

        if tasks:
            print("Task {} done.".format(Q))
        else:
            print("Task {} is failed...".format(Q))

        """
        保存構成
        task_i.txt：i個目の入力サンプル
        ans_i.txt：i個目の入力サンプルに対するこたえ

        実行したディレクトリ
            - コンテスト名のディレクトリ
                - A（ディレクトリ）
                  - task_1.txt
                  - task_2.txt
                  - ans_1.txt
                  - ans_1.txt

                - B
                  - task_1.txt
                  - ans_1.txt
                - C
                  - task_a.txt
                ...
        """



def main(args):
    session = login()

    samples = getSample(session, args.url)
    
    directory = args.url.split("/")[-1]#コンテスト名
    writeSamplesToFile(samples, directory)


if __name__ == "__main__":
    args = parseArgs()
    main(args)

