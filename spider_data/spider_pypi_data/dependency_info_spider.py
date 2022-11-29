import re
from bs4 import BeautifulSoup
from selenium import webdriver
from spider_data.spider_pypi_data.packages_spider import list_split
from utils import pypi_utils
from model.package_version_usage import PkgVersionUsage
from utils import files_utils
from model.package import Package


class DependencyInfoSpider:
    # chromedriver_path = "D:\\chromedriver_win32\\chromedriver.exe"
    def __init__(self, chromedriver_path):
        self.chromedriver_path = chromedriver_path

    def get_library_usage_stats(self, package_name):
        versions = []
        usage_list = []
        url = r'https://libraries.io/pypi/' + package_name + r'/usage'
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        browser = webdriver.Chrome(executable_path=self.chromedriver_path, chrome_options=chrome_options)
        try:
            browser.get(url)
        except Exception as e:
            print("no usage" + str(e))
            return None
        tr_list = browser.find_elements_by_class_name('qtr')
        for tr in tr_list:
            version = tr.find_elements_by_tag_name('th')[0].text
            usage_stats = tr.find_elements_by_tag_name('p')[0].text
            versions.append(version)
            usage_list.append(usage_stats)
        browser.close()
        return versions, usage_list

    def spider_all_version_usage(self, split_group=10, group_num=0, split_state=False):
        results = Package.package_equ_filler(columns=["package_name"], distinct=True)
        if split_state:
            step_length = int(len(results) / split_group)
            group_list = list_split(results, step_length)
            group = group_list[group_num]
        else:
            group = results
        i = 1
        for result in group:
            print(str(i) + ' : ' + str(len(group)))
            i = i + 1
            package_name = result['package_name']
            if PkgVersionUsage.is_spider(package_name):
                continue
            versions, usage_list = self.get_library_usage_stats(package_name)
            version_usage_dict = deal_version_usage(versions, usage_list, package_name)
            for version, usage in version_usage_dict.items():
                PkgVersionUsage.update_version_usage(package_name, version, usage)
            print('-' * 50)

    # 爬取一个包的version_usage
    def spider_package_version_usage(self, package_name):
        versions, usage_list = self.get_library_usage_stats(package_name)
        version_usage_dict = deal_version_usage(versions, usage_list, package_name)
        for version, usage in version_usage_dict.items():
            PkgVersionUsage.update_version_usage(package_name, version, usage)


# 处理从libraries网站爬取的版本名
def deal_libraries_version(version_str):
    version_str = re.sub("[^A-Za-z0-9.]", "", version_str)
    characters = version_str.split('.')
    version = ''
    for character in characters:
        if character != '':
            version += character + '.'
    version = version[:-1]
    return version


# 将usage转为适用的版本号
def deal_version_usage(versions, usage_list, package_name):
    version_usage_dict = {}
    print(package_name)
    for i in range(len(versions)):
        version = versions[i]
        if '<=' in version or '==' in version:
            version = deal_libraries_version(version)
        elif '>' in version:
            pypi_util = pypi_utils.PYPIUtils()
            version = pypi_util.find_newest_version(package_name)
        elif '<' in version:
            version = deal_libraries_version(version)
            utils = pypi_utils.PYPIUtils()
            version = utils.find_elder_version(package_name, version)
        else:
            print(version + '  ' + '未发现<>=等符号')
            version = deal_libraries_version(version)
        version_list = list(version_usage_dict.keys())
        if version not in version_list:
            usage = usage_list[i]

        else:
            usage_num = float(version_usage_dict[version].replace('%', '')) + float(usage_list[i].replace('%', ''))
            usage = str(usage_num) + '%'
        if version:
            print('处理前：' + versions[i] + '-' + usage_list[i] + '   处理后：' + version + '-' + usage)
            version_usage_dict.update({version: usage})
    return version_usage_dict


# 爬取依赖包版本表格
def spider_dependency_version():
    results = Package.package_equ_filler(columns=['package_name'], distinct=True)
    for item in results:
        pypi_util = pypi_utils.PYPIUtils()
        versions = pypi_util.get_package_versions(item.lower())
        for version in versions:
            PkgVersionUsage.insert(item, version, '')
            print(item + " : " + version)


# 将下载的包版本更新到version——usage中
def get_dependency_version():
    result = results = Package.package_equ_filler(columns=['package_name'], distinct=True)
    for item in result:
        version = item['version']
        name = item['package_name']
        if not PkgVersionUsage.is_exist(name, version):
            PkgVersionUsage.insert(name, version, '')
            print(name + " : " + version)


# 获取pypi上libraries库的Meta区域信息
def get_package_meta_info_pypi(package_name, version):
    pypi_util = pypi_utils.PYPIUtils()
    html_text = pypi_util.get_project_description_html(package_name, version)
    if html_text:
        soup = BeautifulSoup(html_text, 'lxml')
    else:
        return ''
    sidebar_sections = soup.find_all('div', class_='sidebar-section')
    for section in sidebar_sections:
        h3 = section.find('h3').text
        if h3 == 'Meta':
            return section.text
    return ''


def get_require_python_version(package_name, version):
    try:
        meta_info = get_package_meta_info_pypi(package_name, version)
    except Exception as e:
        return
    if meta_info != '':
        python_require_info = re.search(r'Requires:(.*?)\n', meta_info)
        if python_require_info:
            str_version = python_require_info.group(1)
        else:
            str_version = ''
            print(package_name + '  ' + version + '  无')
        Package.update_package_support_python_without_whl(str_version,package_name,version)


def spider_require_python_version():
    results = Package.package_equ_filler(columns=["package_name", "package_version"], distinct=True)
    finish_list = files_utils.get_file_content("./finish_require_python_spider.txt")
    for item in results:
        package_name = item['package_name']
        package_version = item['version']
        name = package_name + '-' + package_version
        if name in finish_list:
            continue
        print(package_name)
        print(package_version)
        get_require_python_version(package_name, package_version)
        files_utils.txt_write_into("./finish_require_python_spider.txt", name + '\n')


if __name__ == '__main__':
    # get_dependency_version()
    # spider_all_version_usage()
    # filter_inconsistent_package_version()
    # spider_package_version_usage('certifi')
    # versions, usage_list = get_library_usage_stats('numpy')
    # get_require_python_version('torchvision', '0.1.6')
    spider_require_python_version()
