from utils import files_utils
from model.package import Package
from utils import pypi_utils
from bs4 import BeautifulSoup
import os
from utils.pypi_utils import PYPIUtils
from build_envirement import deal_package_reqs
from model.pipeline_dependency import PipelineDeps
import ssl
import wget

ssl._create_default_https_context = ssl._create_unverified_context


class PackageSpider:
    def __init__(self, package_save_path):
        self.package_save_path = package_save_path

    # 下载package及版本对应的包
    # param：
    # os_names :
    #   例：  ['macos_x86', 'macos_x64', 'macos_x86_64','linux_x86_64']
    # file_formats :
    #   例：  ['.whl', '.zip', 'tar.gz']
    def download_package_version(self, package_name, package_version, os_names, file_formats):
        date_html = ''
        url = 'https://pypi.org/project/' + package_name + '/' + package_version + '/#files'
        try:
            date_html = pypi_utils.get_page(url)
        except Exception as e:
            print("parse_first_page url error " + str(e))
            pass
        hrefs = get_file_download_url_from_pypi(date_html)
        if not hrefs:
            return
        update_time = get_file_update_time_from_pypi(date_html)
        for href in hrefs:
            package_file = href[1]
            url = href[0]
            os_name = deal_package_reqs.get_whl_package_file_support_os(package_file)
            file_format = get_file_format(package_file)
            if (os_name and os_name not in os_names) or file_format not in file_formats:
                continue
            support_python = deal_package_reqs.get_whl_package_file_support_python(package_file)
            pkg = Package(package_name=package_name, package_version=package_version,
                                  package_file=package_file, support_python=support_python,
                                  version_date=update_time, support_os=os_name)
            if not pkg.is_exist_in_package():
                try:
                    download_file(url, package_file, self.package_save_path)
                    pkg.insert_into_packages()
                except Exception as e:
                    print(str(e) + "download error:", package_file)
                    pass
            else:
                print(package_file + "  have exist in database.")

    def download_package(self, package_name, os_names, file_formats):
        utils = PYPIUtils()
        version_list = utils.get_package_versions(package_name)
        for version in version_list:
            self.download_package_version(package_name, version, os_names, file_formats)


# 获取 pypi 网站上的URL
# 新加入
def get_file_download_url_from_pypi(date_html):
    soup = BeautifulSoup(date_html, 'html.parser')
    download_table = soup.find('div', id='files')
    try:
        tr = download_table.find_all(class_="card file__card")
        hrefs = []
        for j in tr[:]:
            name = j.find_all('a')[0].get_text().replace('\r', '').strip()
            a_element = j.find_all('a')[0]
            href = a_element.get('href')
            href = str(href).replace('\r', '').strip()
            if href != '':
                hrefs.append([href, name])
        return hrefs
    except Exception as e:
        print("get_file_download_url_from_pypi error :" + str(e))
        return []


# 获取包的更新日期
# 新加入
def get_file_update_time_from_pypi(date_html):
    soup = BeautifulSoup(date_html, 'html.parser')
    tr = soup.find_all('p', class_='file__meta')
    time = tr[0].find_all('time')[0]
    update_time = time.get('datetime')
    update_time = update_time.replace('T', " ").replace('+0000', "")
    return update_time


# 下载文件
def download_file(url, download_file_name, download_path):
    filename = download_path + '/' + download_file_name
    if not os.path.exists(filename):
        print(url, filename)
        wget.download(url, filename)
        # urllib.request.urlretrieve(url, filename)
    else:
        print(download_file_name + ' have downloaded skip.')


# 获取文件的格式
def get_file_format(download_file_name):
    if '.tar.gz' in download_file_name:
        return '.tar.gz'
    else:
        return download_file_name.split('.')[-1].strip()


# 将带文件名与其版本写入数据库
def spider_all_packages(package_download_path, package_list, os_names, file_formats):
    state = False
    for package_name in package_list:
        finish_list = files_utils.get_file_content("./have_download_packages.txt")
        if package_name in finish_list:
            continue
        state = True
        try:
            pkg_spider = PackageSpider(package_download_path)
            pkg_spider.download_package(package_name, os_names, file_formats)
            files_utils.txt_write_into("./have_download_packages.txt", package_name + '\n')
        except Exception as e:
            print(str(e))
            pass
    return state


# 数组划分
def list_split(items, n):
    return [items[i:i + n] for i in range(0, len(items), n)]


def spider_packages_by_download_name_list(download_file_list, download_path):
    for item in download_file_list:
        result = Package.package_equ_filler(pkg_file=item,columns=['package_name, package_version'])
        if result is None:
            continue
        else:
            result = result[0]
        package_name = result.package_name
        package_version = result.package_version
        date_html = ''
        url = 'https://pypi.org/project/' + package_name + '/' + package_version + '/#files'
        try:
            date_html = pypi_utils.get_page(url)
        except Exception as e:
            print("parse_first_page url error " + str(e))
            pass

        hrefs = get_file_download_url_from_pypi(date_html)
        if not hrefs:
            continue

        for href in hrefs:
            download_file_name = href[1]
            if download_file_name != item:
                continue
            url = href[0]
            try:
                download_file(url, download_file_name, download_path)
            except Exception as e:
                print(str(e) + "download error:", download_file_name)
                pass


# 爬取项目的直接依赖
# split_num : 划分成几部分进行爬取
# num 当前处于划分的第几部分
def spider_project_dependency_packages(package_download_path, split_num, num, os_names, file_formats):
    data = PipelineDeps.filter(columns=['pipeline_dep'], distinct=True)
    step_length = int(len(data) / split_num)
    group_list = list_split(data, step_length)
    packages = group_list[num]
    spider_all_packages(package_download_path, packages, os_names, file_formats)


# 爬取package的依赖包
def spider_package_dependency_packages(package_download_path, split_num, num, os_names, file_formats):
    data = Package.get_all_package_dependencies()
    step_length = int(len(data) / split_num)
    group_list = list_split(data, step_length)
    packages = group_list[num]
    spider_all_packages(package_download_path, packages, os_names, file_formats)


if __name__ == '__main__':
    # 使用
    package_save_folder = "D:\pypi_packages"
    os_names = ["win_x64", "win_x86_64", "win_x32_64", '']
    file_formats = [".whl", '.zip', '.tar.gz']
    # 爬取单个包
    pkg_spider = PackageSpider(package_save_folder)
    pkg_spider.download_package("scikit-learn", os_names, file_formats)

    # 爬取项目的直接依赖包
    # spider_project_dependency_packages(package_save_folder, 1, 0, os_names, file_formats)
    # 爬取间接依赖包
    # spider_package_dependency_packages(package_save_folder, 1, 0, os_names, file_formats)

