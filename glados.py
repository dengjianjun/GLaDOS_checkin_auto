import requests, json, os

if __name__ == '__main__':
    # pushplus秘钥
    sckey = os.environ.get("PUSHPLUS_TOKEN", "")
    sendContent = ''
    
    # 获取 glados 账号 cookie
    cookies = os.environ.get("GLADOS_COOKIE", "").split("&")
    if not cookies or cookies[0] == "":
        print('未获取到 GLADOS_COOKIE 变量')
        exit(0)

    url = "https://glados.rocks/api/user/checkin"
    url2 = "https://glados.rocks/api/user/status"
    referer = 'https://glados.rocks/console/checkin'
    origin = "https://glados.rocks"
    useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    payload = {
        'token': 'glados.one'
    }
    headers_base = {
        'referer': referer,
        'origin': origin,
        'user-agent': useragent,
        'content-type': 'application/json;charset=UTF-8'
    }

    for cookie in cookies:
        headers = headers_base.copy()
        headers['cookie'] = cookie
        
        checkin = requests.post(url, headers=headers, data=json.dumps(payload))
        state = requests.get(url2, headers=headers)
        
        state_json = state.json()
        if 'data' not in state_json:
            print(f"Cookie 已失效或接口返回异常: {state_json}")
            if sckey != "":
                requests.get(f'http://www.pushplus.plus/send?token={sckey}&content=GLaDOS_Cookie已失效')
            exit(1)

        # 强制转为 str 后再按小数点截取整数部分，兼容 int / float / str
        time = str(state_json['data']['leftDays']).split('.')[0]
        email = state_json['data']['email']
        
        if 'message' in checkin.text:
            mess = checkin.json()['message']
            print(f"{email}----结果--{mess}----剩余({time})天")
            sendContent += f"{email}----{mess}----剩余({time})天\n"
        else:
            if sckey != "":
                requests.get(f'http://www.pushplus.plus/send?token={sckey}&content={email} cookie已失效')
            print('cookie已失效')

    if sckey != "" and sendContent != "":
        requests.get(f'http://www.pushplus.plus/send?token={sckey}&title=GLaDOS签到成功&content={sendContent}')
