"""Utils"""
from functools import wraps
import time
import random


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
