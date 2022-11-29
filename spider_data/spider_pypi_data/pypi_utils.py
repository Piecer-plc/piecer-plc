import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import utils.deal_version_utils


def get_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0;Win64;x64) AppleWebKit/537.36 (KHTML, likeGecko) '
                      'Chrome/74.0.3729.157 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


class PYPIUtils:
    url = 'https://pypi.org/project/'

    # 查询所有版本
    def get_package_versions(self, package_name):
        versions = []
        url = r'https://pypi.org/project/' + package_name + r'/#history'
        req = requests.get(url)
        soup = BeautifulSoup(req.text, 'lxml')
        versions_tag = soup.find_all('p', class_='release__version')
        for v in versions_tag:
            version_str = v.get_text()
            if 'pre-release' in version_str:
                continue
            if version_str != '':
                version_str = version_str.replace('\n', '').replace(' ', '')
            if 'yanked' in version_str:
                version_str = version_str.replace('yanked', '')
            versions.append(version_str)
        return versions

    # 查找小于当前版本的最新版本
    def find_elder_version(self, filename, file_version):
        versions = self.get_package_versions(filename)
        list_num = len(versions)
        for n in range(list_num):
            if file_version != versions[n]:
                if file_version == utils.deal_version_utils.compare_newer_version(file_version, versions[n]):
                    return versions[n]
                else:
                    continue
            elif file_version == versions[n] and n+1 < list_num:
                return versions[n+1]
            else:
                raise OverflowError("无小于当前版本的版本存在")

    # 查询最新版本到当前版本之间所有版本
    def find_current_to_latest_all_version(self, filename, file_version):
        versions = self.get_package_versions(filename)
        list_num = len(versions)
        temp_list = []
        for n in range(list_num):
            if file_version != versions[n]:
                temp_list.append(versions[n])
            elif file_version == versions[n]:
                break
        return temp_list

    # 查询当前版本是否存在
    def is_exist_in_pypi(self, filename, file_version):
        versions = self.get_package_versions(filename)
        if file_version in versions:
            return True
        else: 
            return False

    # 查询最新版本
    def find_newest_version(self, filename):
        versions = self.get_package_versions(filename)
        return versions[0]

    # 获取library的project_description 界面
    def get_project_description_html(self, package_name, version):
        url = self.url + package_name + '/' + version
        response_txt = get_page(url)
        return response_txt
