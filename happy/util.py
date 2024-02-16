"""Utils"""
from functools import wraps
import requests
import time
import random
import re
import cloudscraper
import capsolver
from PIL import Image
from PIL import ImageSequence
from happy.dddocr import DdddOcr



def merge_path(path):
    """_summary_

    Args:
        path (_type_): _description_

    Returns:
        _type_: _description_
    """
    if path is None:
        return None
    length = len(path)
    if length == 1:
        return path
    merged_path = [path[0]]
    for i in range(1, length - 1):
        pre_x, pre_y = path[i - 1]
        cur_x, cur_y = next_x, next_y = path[i]
        next_x, next_y = path[i + 1]
        if next_x - cur_x != cur_x - pre_x or next_y - cur_y != cur_y - pre_y:
            merged_path.append(path[i])
    merged_path.append(path[-1])
    return merged_path


def b62(number):
    """_summary_

    Args:
        number (_type_): _description_

    Raises:
        ValueError: _description_

    Returns:
        _type_: _description_
    """
    # 62 进制字符集
    characters = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # 判断输入是否为非负整数
    if not isinstance(number, int) or number < 0:
        raise ValueError("Input must be a non-negative integer")

    # 特殊情况：如果输入为0，则直接返回第一个字符
    if number == 0:
        return characters[0]

    base62 = ""
    while number:
        number, remainder = divmod(number, 62)
        base62 = characters[remainder] + base62

    return base62


def bet(probability):
    """probability% 返回True"""
    # 生成0到100之间的随机数
    random_num = random.randint(0, 100)

    # 判断随机数是否小于等于给定的概率
    if random_num <= probability:
        return True
    return False


def execute_every_second(second):
    """_summary_

    Args:
        second (_type_): _description_
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            elapsed_time = current_time - wrapper.last_execution_time

            if elapsed_time >= second:
                result = func(*args, **kwargs)
                wrapper.last_execution_time = current_time
                return result
            print(
                f"Function {func.__name__} throttled. Wait for {second - elapsed_time:.2f} seconds."
            )
            return None

        wrapper.last_execution_time = 0  # 每个函数有独立的上次执行时间
        return wrapper

    return decorator


def timer(func):
    """函数计时器

    Args:
        func (_type_): _description_
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录函数开始时间
        result = func(*args, **kwargs)  # 执行被装饰的函数
        end_time = time.time()  # 记录函数结束时间
        print(f"函数 {func.__name__} 运行时间: {end_time - start_time} 秒")
        return result
    return wrapper

def solve_captcha(url) -> bool:
    """_summary_

    Args:
        url (_type_): _description_
    """
    scraper = cloudscraper.create_scraper()
    scraper.headers["Cache-Control"] = "no-cache"

    # request main_page
    main_page_text = scraper.get(url).text
    matches = re.findall(r'data-sitekey="([^"]+)"', main_page_text)
    if matches:
        print("data-sitekey:", matches[0])
        sitekey = matches[0]
    else:
        print("页面有误或反爬检测")
        return False

    matches = re.findall(r'updateseccode\(\'([^"]+)\',', main_page_text)
    if matches:
        print("sid:", matches[0])
        sid = matches[0]
    else:
        print("页面有误或反爬检测")
        return False

    # request captcha image
    captcha_url = "https://www.bluecg.net/misc.php?mod=seccode&idhash=" + sid
    scraper.headers["Referer"] = url
    for i in range(5):
        captcha_response = scraper.get(captcha_url)
        captcha_image_buffer = captcha_response.content
        with open("code.gif", "wb") as f:
            f.write(captcha_image_buffer)
        img = Image.open("code.gif")
        max_duration = 0
        for frame in ImageSequence.Iterator(img):
            duration = frame.info["duration"]
            if duration > max_duration:
                frame.save("code.png")
                max_duration = duration

        # recognize captcha image
        dddocr = DdddOcr()
        with open("code.png", "rb") as f:
            image_bytes = f.read()
            verifycode = dddocr.classification(image_bytes)

        checked_res = scraper.get(
            f"https://www.bluecg.net/misc.php?mod=seccode&action=check&inajax=1&modid=plugin::gift&secverify={verifycode}"
        ).text

        if "succeed" in checked_res:
            print("验证码识别成功")
            break
        print(f"验证码识别错误，尝试第{i+1}次")
        if i==4:
            return False

    # solve recaptcha
    capsolver.api_key = "CAP-0C304B4D66688AA0ABE2C8842DBFEAD3"
    solution = capsolver.solve(
        {
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": url,
            "websiteKey": sitekey,
        }
    )

    g_recaptcha_response = solution["gRecaptchaResponse"]
    user_agent = solution["userAgent"]
    if not g_recaptcha_response or not user_agent:
        print("capsolver not work")
        return False

    print(g_recaptcha_response)
    print(user_agent)
    data = {
        "g-recaptcha-response": g_recaptcha_response,
        "seccodehash": sid,
        "seccodemodid": "plugin::gift",
        "seccodeverify": verifycode,
        "submit": "",
    }

    res = scraper.post(url, data=data)
    print(res)
    return True

def send_wechat_notification(content):
        """_summary_

        Args:
            content (_type_): _description_
        """

        url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=e0ce689b-5a47-4ae2-ab5e-0539268956d7"
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            },
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers, timeout=1000)

        if response.status_code == 200:
            print("Markdown message sent successfully.")
        else:
            print(
                "Failed to send Markdown message. Status code:",
                response.status_code,
            )