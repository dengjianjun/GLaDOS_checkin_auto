import os
import json
import requests

def push_ftqq(sckey, title, desp):
    """通过方糖 (sctapi.ftqq.com) 推送微信通知"""
    if not sckey:
        print("未检测到方糖 SendKey，跳过微信推送。")
        return
    
    # 使用 https 协议与 params/data 自动编码，防止换行符 \n 破坏 URL
    api_url = f"https://sctapi.ftqq.com/{sckey}.send"
    payload = {
        "title": title,
        "desp": desp
    }
    try:
        resp = requests.post(api_url, data=payload, timeout=15)
        print(f"方糖推送响应: {resp.text}")
    except Exception as err:
        print(f"方糖推送请求异常: {err}")

def main():
    # 自动兼容原工作流的 PUSHPLUS_TOKEN 以及常见的 SCKEY / SENDKEY 变量名
    sckey = (
        os.environ.get("PUSHPLUS_TOKEN")
        or os.environ.get("SERVERCHAN_SCKEY")
        or os.environ.get("SENDKEY")
        or os.environ.get("SCKEY")
        or ""
    ).strip()

    raw_cookies = os.environ.get("GLADOS_COOKIE", "").strip()
    if not raw_cookies:
        print("未获取到 GLADOS_COOKIE 环境变量，程序退出。")
        return

    cookie_list = [c.strip() for c in raw_cookies.split("&") if c.strip()]
    
    checkin_url = "https://glados.rocks/api/user/checkin"
    status_url = "https://glados.rocks/api/user/status"
    
    base_headers = {
        "referer": "https://glados.rocks/console/checkin",
        "origin": "https://glados.rocks",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "content-type": "application/json;charset=UTF-8"
    }
    
    send_content = ""
    last_email = "GLaDOS"

    for idx, cookie in enumerate(cookie_list, 1):
        headers = base_headers.copy()
        headers["cookie"] = cookie
        
        try:
            checkin_resp = requests.post(
                checkin_url, 
                headers=headers, 
                data=json.dumps({"token": "glados.one"}),
                timeout=15
            )
            status_resp = requests.get(status_url, headers=headers, timeout=15)
            status_data = status_resp.json()
        except Exception as e:
            err_msg = f"账号 {idx} 网络请求异常: {e}"
            print(err_msg)
            push_ftqq(sckey, "GLaDOS 签到请求异常", err_msg)
            continue

        # 校验状态接口是否正常返回 data 字段
        if "data" not in status_data:
            fail_msg = f"账号 {idx} Cookie 已失效或接口异常，返回: {status_data}"
            print(fail_msg)
            push_ftqq(sckey, "GLaDOS Cookie已失效", fail_msg)
            continue

        # 强制转换为字符串再截取整数天数，避免 int 类型无 split 报错
        left_days = str(status_data["data"].get("leftDays", "未知")).split(".")[0]
        email = status_data["data"].get("email", f"Account_{idx}")
        last_email = email

        if "message" in checkin_resp.text:
            mess = checkin_resp.json().get("message", "无返回消息")
            line_log = f"{email}----结果--{mess}----剩余({left_days})天"
            print(line_log)
            # 方糖 Markdown 需要两个换行符才会折行显示
            send_content += f"{line_log}\n\n"
        else:
            print(f"{email} cookie已失效")
            push_ftqq(sckey, f"{email} cookie已失效", f"签到响应异常: {checkin_resp.text}")

    # 汇总推送签到成功结果
    if send_content:
        title = f"{last_email}签到成功" if len(cookie_list) == 1 else "GLaDOS多账号签到成功"
        push_ftqq(sckey, title, send_content)

if __name__ == "__main__":
    main()
