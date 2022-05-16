import httpx, json, os, pyfiglet
from time import time
from random import choice
from captchatools import captcha_harvesters
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
from fake_useragent import UserAgent

with open('./config.json') as fp:
    config = json.load(fp)

captchakey = config["CaptchaKey"]
captchaApi = config["CaptchaApi"]
password = config["Password"]
mailDomain = config["MailDomain"]


Failed = 0
Created = 0


class bcolors:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


ua = UserAgent()
#def RandomUseragent():
#    return ua.random I Do not recommend this, heavily reduces success rates.


def SolveCaptcha():
    captchaToken = captcha_harvesters(solving_site=captchaApi, 
    api_key=f"{captchakey}", 
    sitekey=f"3e48b1d1-44bf-4bc4-a597-e76af6f3a260", 
    captcha_type="hcap", 
    captcha_url="https://tellonym.me/")
    hcapresolution = captchaToken.get_token() # Gets the hcaptcha token
    return hcapresolution


def GetProxy():
    with open('./Data/proxies.txt', 'r') as temp_file:
        proxy = [line.rstrip('\n') for line in temp_file]
    return proxy

proxy = GetProxy()
proxy_pool = cycle(proxy )

def GetProxies():
    proxy = next(proxy_pool)
    if len(proxy.split(':')) == 4:
        splitted = proxy.split(':') 
        return f"{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}" # Converts ip:port:user:pass format to user:pass@ip:port
    return proxy

Time = time()
def register():
    global Created
    global Failed
    while True:
        try:
            os.system(f"title Clips TellonymCreator  / {round(Created / ((time() - Time) / 60))}\m / Success {Created} / Failed {Failed}")
            with open('./Data/usernames.txt', 'r') as u:
                username = choice(u.readlines()).strip()
            email = username + "@" + mailDomain
            client = httpx.Client(
                headers={'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8', 'authority': 'api.tellonym.me', 'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Microsoft Edge";v="100"','origin': 'https://tellonym.me', 'accept': 'application/json','content-type': 'application/json;charset=utf-8','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','sec-fetch-dest': 'empty','sec-fetch-mode': 'cors','sec-fetch-site': 'same-site','tellonym-client': 'web:0.62.1','user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'}, 
                proxies=f"http://"+GetProxies()
            )
            res = client.post("https://api.tellonym.me/accounts/register", json={'deviceName': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36','deviceType': 'web','lang': 'en','hCaptcha': SolveCaptcha(),'email': email,'password': password,'username': username,'limit': 25,}, timeout=30)
            if res.status_code in [503, 400, 401, 403, 429]:
                print(f'{bcolors.RED}Failed to Create Account: {res} {bcolors.RESET}')
            else:
                accessToken = res.json()["accessToken"]
                print(f'{bcolors.GREEN}Successfully Created Account: {email}:{password} {bcolors.RESET}')
                Created +=1
                with open("./out/Accounts.txt", "a") as f:
                    f.write(f'{email}:{password}:{accessToken}\n')
                    f.close

                with open("./out/tokens.txt", "a") as f:
                    f.write(f'{accessToken}\n')
                    f.close
        except:
            Failed+=1
            print(f'{bcolors.RED}Failed to Create Account: {res} {bcolors.RESET}')
if __name__ == "__main__":
    os.system("cls")
    print(pyfiglet.figlet_format(f"Clips Tello Creator"))
    threadAmount=input(f'{bcolors.BLUE}Thread Amount: {bcolors.RESET}')
    os.system("cls")
    threadAmount = 1 if threadAmount == "" else int(threadAmount)
    threads = []
    with ThreadPoolExecutor(max_workers=threadAmount) as tello:
        for x in range(threadAmount):
            tello.submit(register)
