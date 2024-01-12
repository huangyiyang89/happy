"""mem"""
import happy.mem




class Service:
    """add mem"""

    def __init__(self, mem: happy.mem.CgMem) -> None:
        self.mem = mem

    def update(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self

    def base62_encode(self,number):
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