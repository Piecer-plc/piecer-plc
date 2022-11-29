import os
from model.package import Package
from bs4 import BeautifulSoup
from packaging.utils import parse_wheel_filename
import wget
from spider_data.spider_pypi_data.pypi_utils import get_page
from spider_data.spider_pypi_data.packages_spider import get_file_update_time_from_pypi


def get_update_time(package_name, version):
    url = 'https://pypi.org/project/' + package_name + '/' + version + '/#files'
    date_html = get_page(url)
    update_time = get_file_update_time_from_pypi(date_html)
    return update_time


class PytorchPkgSpider:
    URL = "https://download.pytorch.org/whl/torch_stable.html"

    def __init__(self, save_path=None, save_local=False, save_database=True):
        if save_local and save_path is None:
            print("If you want download these packages, please set save_path, or set save_local=False.")
        self.save_path = save_path
        self.save_local = save_local
        self.save_database = save_database

    def __get_infos(self):
        infos ={}
        content = get_page(self.URL)
        soup = BeautifulSoup(content, 'html.parser')
        tr_list = soup.findAll('a')
        for item in tr_list:
            href = item.get("href")
            download_url = self.URL + "/" + href
            file_name = item.text
            if "%2B" in file_name:
                file_name = file_name.replace("%2B", "+")
            name_parts = file_name.split('/')
            if len(name_parts) == 1:
                deal_name = name_parts[0]
            else:
                deal_name = name_parts[1]
            name, ver, build, tags = parse_wheel_filename(deal_name)
            ver = str(ver)
            if "+" in ver:ver = ver.split("+")[0]
            tag = list(tags)[0]
            interpreter = tag.interpreter
            platform = tag.platform
            item_info ={
                "package_name": name,
                "package_version": ver,
                "download_url": download_url,
                "interpreter": interpreter,
                "platform":platform
            }
            if (name, ver) in infos:
                infos[(name,ver)].update({file_name:item_info})
            else:
                infos.update({(name,ver):{file_name:item_info}})
        return infos

    def __download(self, url, file_name):
        save_path = os.path.join(self.save_path, file_name)
        wget.download(url,save_path)
        print("download>>>>:\n" + file_name, "\nsave to:" + save_path)

    def spider_package(self, package_name, versions=None):
        infos = self.__get_infos()
        if versions:
            info_list = [infos[(package_name, ver)] for ver in versions]
        else:
            info_list = []
            for key in infos:
                if key[0] == package_name:info_list.append(infos[key])
        if self.save_local:
            for item in info_list:
                for file_name, info in item.items():
                    self.__download(info['download_url'], file_name)
        if self.save_database:
            for item in info_list:
                for file_name, info in item.items():
                    update_time = get_update_time(info['package_name'],info['package_version'])
                    Package(package_name=info['package_name'],
                            package_version=info['package_version'],
                            package_file=file_name,
                            version_date=update_time,
                            support_os=info['platform'],
                            support_python=info["interpreter"]).insert_into_packages()


if __name__ == "__main__":
    spider = PytorchPkgSpider(save_database=True)
    spider.spider_package('torchvision',["0.11.0"])
