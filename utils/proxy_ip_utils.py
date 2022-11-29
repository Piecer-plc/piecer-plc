import random
import telnetlib
import requests


class NetWorkError:
    pass


class ProxyIPUtils:
    # proxy_url 芝麻代理上获得IP的网页链接
    ip = None
    port = None
    ip_txt_path = 'D:\\pipeline\\ip.txt'
    proxy_ip_len = 0
    ip_list = []

    def __init__(self, proxy_url=None):
        if proxy_url is None:
            self.init_ip_list_from_local()
        else:
            self.proxy_url = proxy_url
            self.__get_proxy_ip_list()

    def __get_proxy_ip_list(self):
        r = requests.get(self.proxy_url)
        ip_list = (r.text.replace('\r', '').replace(' ', '')).split('\n')
        self.__save_ip_to_local(r.text.replace('\r', '').replace(' ', ''))
        max_len = len(ip_list)
        self.proxy_ip_len = max_len - 2
        self.ip_list = ip_list

    def init_ip_list_from_local(self):
        with open(self.ip_txt_path,'r') as f:
            content = f.read()
            f.close()
        ip_list = content.split('\n')
        max_len = len(ip_list)
        self.proxy_ip_len = max_len - 2
        self.ip_list = ip_list

    def __create_random_proxy_ip(self):
        random_num = random.randint(0, self.proxy_ip_len)
        proxy_ip = self.ip_list[random_num]
        self.ip = proxy_ip.split(':')[0]
        self.port = proxy_ip.split(':')[1]

    def __save_ip_to_local(self, content):
        with open(self.ip_txt_path, 'w') as f:
            f.write(content)
            f.close()

    def __is_proxy_ip_effective(self):
        try:
            proxy = {
                "https": "https://" + self.ip + ':' + self.port
            }
            requests.get('https://www.kaggle.com:443', proxy)
            return True
        except Exception as e:
            print(str(e))
            return False

    def get_effective_proxy_ip(self):
        for i in range(1000):
            self.__create_random_proxy_ip()
            if self.__is_proxy_ip_effective():
                return self.ip, self.port
        return '0', '0'


