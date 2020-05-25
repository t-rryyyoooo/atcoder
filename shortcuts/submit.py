import argparse
import sys
import os
from bs4 import BeautifulSoup
import requests
import re

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--language", help="PyPy3", default="pypy3")

    args = parser.parse_args()
    return args

def main(args):
    # Get directory (contest name)
    contestName = (os.getcwd().split("/")[-2]).lower()
    Q = os.getcwd().split("/")[-1].lower()

    # Read source file.
    if os.path.exists("solve.py"):
        f = open("solve.py")
        sourceCode = f.read()
        f.close()
    else:
        print("solve.py is not found.")
        sys.exit()


    # Log in.
    LOGIN_URL = "https://atcoder.jp/login"

    session = requests.session()
    r = session.get(LOGIN_URL)
    s = BeautifulSoup(r.text, "lxml")
    csrf_token = s.find(attrs={"name" : "csrf_token"}).get("value")
    login_info = {
            "csrf_token" : csrf_token, 
            "username" : "Your username", 
            "password" : "Your password"
            }

    result = session.post(LOGIN_URL, data=login_info)
    result.raise_for_status()
    if result.status_code == 200:
        print("Log in!")
    else:
        print("Failed...")
        sys.exit()

    # Submit file.

    submitUrl = "https://atcoder.jp/contests/" + contestName + "/submit"
    html = session.get(submitUrl)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "lxml")
    csrf_token = soup.find(attrs={"name" : "csrf_token"}).get("value")
    taskScreenName = contestName + "_" + Q
    langIdSoup = soup.find(attrs={"id" : "select-lang-" + taskScreenName})
    langIds = langIdSoup.find_all("option")

    languageId = None
    for langId in langIds:
        if re.match(args.language, langId.text):
            languageId = langId.get("value")

    if languageId is None:
        print("{} is not supported.".format(args.language))
        sys.exit()


    submit_info = {
            "data.TaskScreenName" : taskScreenName, 
            "csrf_token" : csrf_token,
            "data.LanguageId" : languageId, 
            "sourceCode" : sourceCode
            }

    submitResult = session.post(submitUrl, data=submit_info)
    submitResult.raise_for_status()
    if submitResult.status_code == 200:
        print("Submitted")
    else:
        print("Failed to submit...")
        sys.exit()
        






    
                  


if __name__ == "__main__":
    args = parseArgs()
    main(args)
