from email.policy import default
from time import sleep
from xmlrpc.server import list_public_methods

from selenium import webdriver
from selenium.webdriver.support.select import Select
import pymysql
import time
import numpy as np
import re
import datetime
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import cn2an

#默认路径
default_save_path_refix = "影视/4k/动漫-持续更新/"
#账号密码
username = 'username'
password = 'password'
#默认寻找元素的超时时间，如果超过5秒都没有找到就会报错
timeout_xhr = 10
#同上，只是这里需要等iframe的数据加载完毕，所以多两秒
timeout_iframe_xhr = 7

mysql_host = 'mysql_host'
mysql_port = 3306
mysql_user = 'mysql_user'
mysql_passwd = 'mysql_passwd'
mysql_database = 'mysql_database'

now_datetime = datetime.date.today()
now_date = now_datetime.strftime("%Y-%m-%d")
now_weekday = datetime.date.today().weekday()
login_189_status = False



#更新数据库,某行的一个数据,调用方法为寻找名称为name的行,寻找名称为XX的行，将其修改为新的数据
def update_cloud_data (name,row_name,data):
    name = "\"" + str(name) + "\""
    row_name = "`" + str(row_name) + "`"
    data = "\'" + str(data) + "\'"
    command = "UPDATE cloud_user SET %s = %s WHERE cloud = %s" % (row_name,data,name)
    #print(command)
    sql.execute(command);
    db.commit()


def update_movie_data (name,row_name,data):
    name = "\"" + str(name) + "\""
    row_name = "`" + str(row_name) + "`"
    data = "\'" + str(data) + "\'"
    command = "UPDATE movie_data SET %s = %s WHERE name = %s" % (row_name,data,name)
    #print(command)
    sql.execute(command);
    db.commit()


def update_movie_data2 (name,row_name,data,row2_name,data2):
    name = "\'" + str(name) + "\'"
    row_name = "`" + str(row_name) + "`"
    data = "\'" + str(data) + "\'"
    row2_name = "`" + str(row2_name) + "`"
    data2 = "\'" + str(data2) + "\'"
    command = "UPDATE movie_data SET %s = %s, %s = %s WHERE name = %s" % (row_name,data,row2_name,data2,name)
    #print(command)
    sql.execute(command);
    db.commit()


def wait_xhr_finnish (xhr_path,timeout = timeout_xhr ) :
    try:
        WebDriverWait(chrome, timeout).until(
            EC.presence_of_element_located((By.XPATH, xhr_path))
        )
        return True
    except Exception as err:
        return False


def wait_iframe_xhr_finnish (iframe,xpath,timeout = timeout_iframe_xhr) :
    try:
        chrome.switch_to.frame(iframe)
        WebDriverWait(chrome, timeout).until(
            EC.visibility_of_element_located((By.XPATH, xpath))
        )
        chrome.switch_to.default_content()
        return True
    except Exception as err:
        print(f'等待网页加载错误：{err}')
        return False


def choose_url(xpath,method = 1):
    pointer = chrome.find_element_by_xpath(xpath)
    if method == 1:
        chrome.execute_script("arguments[0].click();", pointer)
    elif method == 2:
        pointer.click()


def Initializing_variables (i):
    global movie_name
    global movie_info_url
    global movie_update_url
    global movie_url_status
    global movie_movie_name
    global movie_url_path
    global movie_have_episodes
    global movie_save_path
    global movie_share_key
    global movie_update_time
    global movie_update_interval
    global movie_latest_episodes
    movie_name = movie_data[i][0]
    movie_info_url = movie_data[i][1]
    movie_update_url = movie_data[i][2]
    movie_share_key = movie_data[i][3]

    movie_url_path = movie_data[i][4]
    if movie_url_path != None:
        if movie_url_path.startswith(" "):
            movie_url_path = (movie_url_path.strip(" "))
        if movie_url_path.endswith(" "):
            movie_url_path = (movie_url_path.strip(" "))

    if movie_data[i][5].startswith("/"):
        movie_save_path = movie_data[i][5]
        movie_save_path = (movie_save_path.lstrip("/"))
    else :
        movie_save_path = default_save_path_refix + movie_data[i][5]
    if movie_save_path != None:
        if movie_save_path.startswith(" "):
            movie_save_path = (movie_save_path.strip(" "))
        if movie_save_path.endswith(" "):
            movie_save_path = (movie_save_path.strip(" "))

    movie_have_episodes = movie_data[i][6]
    movie_update_time = movie_data[i][7]
    movie_url_status = movie_data[i][8]
    movie_update_interval = movie_data[i][9]
    movie_latest_episodes = movie_data[i][10]

# 建立数据库连接
def connect_mysql():
    try:
        global db
        global sql
        db = pymysql.connect(host=mysql_host, port=mysql_port, user=mysql_user, password=mysql_passwd, charset='utf8mb4')
        print("数据库连接成功")
        sql = db.cursor()
    except Exception as err:
        exit()
        # 如果连接失败则退出


#查询数据
def grep_data ():
    db.select_db(mysql_database)
    global cloud_cookies_189
    sql.execute('SELECT * FROM cloud_user')
    data = sql.fetchall()
    cloud_num = len(data)
    cloud_data = [[0] * 2] * cloud_num
    for i, row in enumerate(data):
        cloud_data[i] = [row[0], row[1]]
        if row[0] == "189" :
            cloud_cookies_189 = row[1]
#查询要更新的动漫
    global movie_data
    global movie_num
    sql.execute('SELECT * FROM movie_data')
    data = sql.fetchall()
    movie_num = len(data)
    movie_data = [[0] * 11] * movie_num
    for i, row in enumerate(data):
        movie_data[i] = [row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10]]


def openchrome():
    print("初始化浏览器")
    options = webdriver.ChromeOptions()
    #options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--single-process')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    #创建浏览器对象,并打开更新地址
    global chrome
    chrome = webdriver.Chrome(options=options)



def whether_update_episodes():
    update_time = movie_update_time.strftime("%Y-%m-%d")
    date1 = datetime.datetime.strptime(now_date[0:10], "%Y-%m-%d")
    date2 = datetime.datetime.strptime(update_time[0:10], "%Y-%m-%d")
    num = (date1 - date2).days
    if num < movie_update_interval:
        print(f"当前最新集数更新小于设置的{movie_update_interval}天,跳过更新")
        return False
    return True


def get_latest_episodes():
    # 判断那个网站,定义元素位置
    chrome.get(movie_info_url)
    global latest_episodes_end
    latest_episodes_end = False

    if "v.qq.com" in movie_info_url:
        if not get_tencent_latest_episodes():
            return False
    elif "iqiyi.com" in movie_info_url:
        if not get_iqiyi_latest_episodes():
            return False
    elif "youku.com" in movie_info_url:
        if not get_youku_latest_episodes():
            return False
    elif "bilibili.com" in movie_info_url:
        if not get_bilibili_latest_episodes():
            return False

    if movie_latest_episodes == False:
        print("更新集数失败")
        return False
    if latest_episodes_end == True :
        update_movie_data(movie_name, "update_interval", 999)
    else :
        update_movie_data(movie_name, "update_interval", update_interval)
    update_movie_data2(movie_name, "latest_episodes", movie_latest_episodes, "update_time", last_update_date)

    return movie_latest_episodes

def get_bilibili_latest_episodes () :
    xpath = '//*[@id="__next"]/div[2]/div/div[3]/div[3]/div[3]/div'
    if wait_xhr_finnish(xpath) == False:
        print("错误:未能获取最新集数,可能是网络波动等问题")
        return False
    url_episodeslist = chrome.find_elements_by_xpath(xpath)
    url_have_episodes = len(url_episodeslist)
    url_episodes_new_list = []
    for i in range(url_have_episodes):
        rule = re.compile("(\d{1,3})\\n(.*)")
        grep_result = rule.search(url_episodeslist[url_have_episodes -i -1 ].text)
        if grep_result != None:
            if  not '预告' in grep_result.group(2):
                num = int(grep_result.group(1))
                global movie_latest_episodes
                movie_latest_episodes = num
                global last_update_date
                last_update_date = now_date
                xpath = '//*[@id="__next"]/div[2]/div/div[2]/div/div[2]/div/div[2]/span[3]'
                pointer = chrome.find_element_by_xpath(xpath)
                if '完结' in pointer.text:
                    global latest_episodes_end
                    latest_episodes_end = True
                return num

def get_youku_latest_episodes():
    xpath = '//*[@id="app"]/div/div[2]/div[2]/div/div/div[2]/div[1]/div[2]/div[1]/div[2]'
    if wait_xhr_finnish(xpath) == False:
        print("错误:未能获取最新集数,可能是网络波动等问题")
        return False
    pointer = chrome.find_element_by_xpath(xpath)
    rule = re.compile("更新至(\d{1,3})")
    grep_result = rule.search(pointer.text)
    if grep_result != None:
        num = int(grep_result.group(1))
        global movie_latest_episodes
        movie_latest_episodes = num
        global last_update_date
        last_update_date = now_date
        if '全' in pointer.text:
            global latest_episodes_end
            latest_episodes_end = True
        global update_interval
        update_interval = 7
        if '电视剧' in chrome.title:
            last_update_date = now_date
            update_interval = 1
        else:
            last_update_date = get_update_date(1)
            update_interval = 7
        return num
    else :
        print(f"错误：未找到最新集数，网站为优酷")
        return False

def get_iqiyi_latest_episodes():
    xpath = '//*[@id="meta_info_bk"]/div/div/div/div/div[2]/div/div[1]/div[2]'
    if wait_xhr_finnish(xpath) == False:
        print("错误:未能获取最新集数,可能是网络波动等问题")
        return False
    choose_url(xpath)
    xpath = '//*[@id="intro_bk"]/div/div/div/div/div[1]/div[2]/div[3]'
    if wait_xhr_finnish(xpath) == False:
        print("错误:未能获取最新集数,可能是网络波动等问题")
        return False
    pointer = chrome.find_element_by_xpath(xpath)
    rule = re.compile("更新至(\d{1,3})集")
    grep_result = rule.search(pointer.text)
    if grep_result != None:
        num = int(re.sub("\D", "", grep_result.group(1)))
    else :
        print(f"错误：未找到最新集数，网站为爱奇艺")
    global last_update_date
    last_update_date = now_date
    global movie_latest_episodes
    if '全' in pointer.text:
        global latest_episodes_end
        latest_episodes_end = True
    global update_interval
    update_interval = 7
    if '电视剧' in chrome.title:
        last_update_date = now_date
        update_interval = 1
    else:
        last_update_date = get_update_date(1)
        update_interval = 7
    movie_latest_episodes = num
    return num
def get_tencent_latest_episodes():
    xpath = '//*[@id="app"]/div[2]/div[2]/div/div[2]/div/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[2]/div[2]/span[1]'
    if wait_xhr_finnish(xpath) == False:
        print("错误:未能获取最新集数,可能是网络波动等问题")
        return False
    pointer = chrome.find_element_by_xpath(xpath)
    num = pointer.text
    num = int(re.sub("\D", "", num))
    global movie_latest_episodes
    movie_latest_episodes = num
    if '全' in pointer.text:
        global latest_episodes_end
        latest_episodes_end = True
    global last_update_date
    global update_interval
    if '电视剧' in chrome.title :
        last_update_date = now_date
        update_interval = 1
    else:
        last_update_date = get_update_date(1)
        update_interval = 7
    return num


def get_update_date(method):
    xpath = '//*[@id="app"]/div[2]/div[2]/div/div[2]/div/div/div[2]/div[1]/div[1]/div[2]/span'
    if method == 1:
        xpath = '//*[@id="app"]/div[2]/div[2]/div/div[2]/div/div/div[2]/div[1]/div[1]/div[2]/span'
        rule = re.compile("周(.)\d")
    wait_xhr_finnish(xpath)
    pointer = chrome.find_element_by_xpath(xpath)
    url_weektime_text = pointer.text
    grep_result = rule.findall(url_weektime_text)
    url_update_time_list_num = len(grep_result)
    week_time_list = []
    if url_update_time_list_num:
        for i in range(url_update_time_list_num):
            if grep_result != None:
                if '日' in grep_result[i]:
                    week_time_list.append(int(7))
                else:
                    week_time_list.append(cn2an.cn2an(grep_result[i]))

    if week_time_list:
        # 因为周日会比周一快,所以需要添加判断
        update_weektime = week_time_list[week_time_list.index(max(week_time_list))] - 1
        if update_weektime != 6:
            update_weektime = week_time_list[week_time_list.index(min(week_time_list))] - 1
        if now_weekday == update_weektime:
            return now_date
        else:
            for i in range(7):
                tmp_date = now_datetime - datetime.timedelta(days=i + 1)
                tmp_date_weekday = tmp_date.weekday()
                if tmp_date_weekday == update_weektime:
                    return tmp_date
                    break

def update_189cloud ():
    global login_189_status
    print("开始登录网盘")
    if login_189_status == False:
        if  login_189_cloud() :
            login_189_status == True
        else:
            print("错误：登录失败，请检查网络或账号密码")
            return False
    chrome.get(movie_update_url)
    chrome.implicitly_wait(5)
    if not get_url_stutas() :
        update_movie_data(movie_name, "url_status", 0)
        return False
    #寻找需要保存的文件
    if  movie_url_path != None :
        getin_url_path()
    if not get_save_file():
        return False
    #寻找需要保存的文件
    if not start_reprint():
        return False
    #最后判断是否更新成功
    return True

def login_189_cloud () :
    if not use_cookies_login():
        use_user_passwd_login()
    global login_189_status
    login_189_status = True
    return True


def use_cookies_login () :
    chrome.get('https://cloud.189.cn/web/login.html')
    if wait_xhr_finnish('//*[@id="udb_login"]') == False:
        print("无法加载登录页面,终止全部更新0")
        err_quit()
        return False
    cookies_list = json.loads(cloud_cookies_189)
    for cookie in cookies_list:
        chrome.add_cookie(cookie)
    chrome.get('https://cloud.189.cn/web/main/file/folder/-11')
    if wait_xhr_finnish('/html/body/div[1]/section/div[1]/div[3]/div[2]'):
        login_189_status = True
        print("使用Cookies登录成功")
        return True
    else :
        if wait_xhr_finnish('//*[@id="udb_login"]') :
            print('登录失败,可能是cookies失效,使用账号密码登录')
            return False
        else :
            print('登录失败:无法加载页面,终止全部更新')
            err_quit()

def use_user_passwd_login ():
    if not wait_iframe_xhr_finnish("udb_login",'//*[@id="tab-qr"]') :
        print('登录失败:无法加载页面,终止全部更新1')
        err_quit()
        return False
    chrome.switch_to.frame("udb_login")
    xpath = '//*[@id="tab-pw"]'
    choose_url(xpath)
    chrome.find_element_by_xpath('//*[@id="userName"]').send_keys(username)
    chrome.find_element_by_xpath('//*[@id="password"]').send_keys(password)
    xpath = '//*[@id="j-agreement-box"]'
    choose_url(xpath)
    xpath = '//*[@id="j-login"]'
    choose_url(xpath)
    chrome.switch_to.default_content()
    if not wait_xhr_finnish('/html/body/div[1]/section/div[1]/div[3]/div[2]'):
        print("登录失败:请检查网络")
        err_quit()
    else:
        print("使用账号密码登录成功,上传当前Cookies")
        global cloud_cookies
        cloud_cookies = chrome.get_cookies()
        cloud_cookies = json.dumps(chrome.get_cookies())
        update_cloud_data("189", "cookies", cloud_cookies)
    return True


#判断网页存活
def get_url_stutas () :
    xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[2]/div[2]/div/div/section/ul/li'
    # 是否需要分享码
    if not wait_xhr_finnish(xpath):
        print("错误:尝试用访问码拼接尝试")
        chrome.get(movie_update_url + "（访问码：" + movie_share_key + "）")
        if not wait_xhr_finnish(xpath):
            print("错误:尝试用访问码访问失败,请检查资源状态")
            return False
    return True


def getin_url_path():
    print("开始进入资源目录")
    getin_path = movie_url_path.split("/")
    path_level = len(getin_path)
    for i in range(path_level):
        xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[2]/div[2]/div/div/section/ul/li'
        list = chrome.find_element_by_xpath(xpath).find_elements_by_xpath("./div/div[1]/div[2]/p/span")
        url_path = len(list)
        for ii in range(url_path):
            if list[ii].text == getin_path[i]:
                xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[2]/div[2]/div/div/section/ul/li['+str(ii+1)+']/div/div[1]/div[2]/p/span'
                choose_url(xpath,2)
                xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[2]/div[2]/div/div/section/ul/li'
                if not wait_xhr_finnish(xpath) :
                    print("错误，未能加载网页中列表")
                    return False
                break
            else :
                if ii +1 == range(url_path):
                    print('错误:未找到资源目录,请检查资源路径')




# 寻找需要保存的文件，并选中
def get_save_file():
    print("开始寻找转存文件")
    xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[2]/div[2]/div/div/section/ul'
    list = chrome.find_element_by_xpath(xpath).find_elements_by_xpath("./li/div/div[1]/div[2]/p")
    url_have_episodes = len(list)
    url_episodes_new_list = []
    for i in range(url_have_episodes):
        choose_sure = False
        # 开始匹配文件名
        rule = re.compile(".*[S,s]\d{1,3}[E,e](\d{1,3}).*\.(mkv|mp4)")
        grep_result = rule.search(list[i].text)
        if grep_result != None:
            choose_sure = True
        else:
            rule = re.compile("(^\d{1,3})\.(mkv|mp4)")
            grep_result = rule.search(list[i].text)
            if grep_result != None:
                choose_sure = True
            else:
                rule = re.compile(".*第(\d{1,3})集.*\.(mkv|mp4)")
                grep_result = rule.search(list[i].text)
                if grep_result != None:
                    choose_sure = True
        if choose_sure == True:
            url_list_episodes = int(grep_result.group(1))
            if url_list_episodes <= movie_latest_episodes and url_list_episodes > movie_have_episodes:
                xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[2]/div[2]/div/div/section/ul/li[' + str(
                i + 1) + ']/label/span/input'
                choose_url(xpath)
                url_episodes_new_list.append(url_list_episodes)

    if url_episodes_new_list:
        global upload_movie_have_episodes
        upload_movie_have_episodes = url_episodes_new_list[url_episodes_new_list.index(max(url_episodes_new_list))]
    else:
        return False
        print("未找到需要保存的文件,可能是还未更新")
    return True

def start_reprint () :
    print("开始选择保存目录")
    xpath ='//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[2]/div[2]/div/div/section/div[1]/div[2]/div[1]/div[2]/div[1]'
    choose_url(xpath)
    xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[2]/div[1]/div/div[1]/div[2]'
    if not wait_xhr_finnish(xpath) :
        print("获取网盘目录失败，请检查网络")
        return False
    cloud_save_path = movie_save_path.split("/")
    cloud_save_path_level = len(cloud_save_path)
    cloud_xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[2]/div[1]/div/div[1]/div[2]/div'
    for i in range(cloud_save_path_level):
        cloud_path_list = chrome.find_elements_by_xpath(cloud_xpath)
        cloud_path_lnum = len(cloud_path_list)
        if cloud_path_lnum != 0:
            for ii in range(cloud_path_lnum):
                if cloud_path_list[ii].text == cloud_save_path[i]:

                    cloud_xpath = cloud_xpath + '[' + str(ii + 1 ) + ']'
                    xpath = cloud_xpath + '/div/div'
                    choose_url(xpath,2)
                    xpath = cloud_xpath + '/div[2]'
                    if i + 1 != cloud_save_path_level:
                        if wait_xhr_finnish(xpath):
                            cloud_xpath = cloud_xpath + '/div[2]/div'
                            break
                        else:
                            print('获取网盘下层目录失败')
                    else:
                        break
                else :
                    if ii +1 == cloud_path_lnum:
                        #xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[2]/div[1]/div/div[1]/div[2]/div[7]/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div/div/div/span/input'
                        #xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[2]/div[1]/div/div[1]/div[2]/div[7]/div[2]/div[2]/div[2]/div[3]/div[2]/div'

                        #xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[2]/div[1]/div/div[1]/div[2]/div[7]/div[2]/div[2]/div[2]/div[3]/div[2]/div[1]/div[2]/div[1]/div/div/div/span/input'
                        xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[3]/div[1]/button[1]'
                        choose_url(xpath)
                        cloud_xpath = cloud_xpath + '[' + str(1) + ']'
                        xpath = cloud_xpath + '/div/div/div/span/input'
                        wait_xhr_finnish(xpath)
                        chrome.find_element_by_xpath(xpath).send_keys(cloud_save_path[i])
                        xpath = cloud_xpath + '/div/div/div/span/div/a[2]'
                        choose_url(xpath)
                        cloud_xpath = cloud_xpath + '/div[2]/div'
                        print("未寻找到保存路径,开始新建文件夹")
        else:
            xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[3]/div[1]/button[1]'
            choose_url(xpath)
            cloud_xpath = cloud_xpath + '[' + str(1) + ']'
            xpath = cloud_xpath + '/div/div/div/span/input'
            wait_xhr_finnish(xpath)
            chrome.find_element_by_xpath(xpath).send_keys(cloud_save_path[i])
            xpath = cloud_xpath + '/div/div/div/span/div/a[2]'
            choose_url(xpath)
            cloud_xpath = cloud_xpath + '/div[2]/div'
            print("未寻找到保存路径,开始新建文件夹")

    xpath = '//*[@id="__qiankun_microapp_wrapper_for_micro_home_share__"]/div/div[6]/section/div/div[3]/div[2]/button[2]'
    choose_url(xpath)
    xpath = '/html/body/div[10]/span/div/div/div/span/span'
    if not wait_xhr_finnish(xpath) :
        xpath = '/html/body/div[4]/div/div[2]/div[1]/p[1]/span'
        pointer = chrome.find_element_by_xpath(xpath)
        url_message = pointer.text
        if url_message != "":
            # 文件存在操作
            xpath = '/html/body/div[4]/div/div[2]/div[2]/label[1] '
            print("发现文件冲突窗口,进行替换处理")
            if wait_xhr_finnish(xpath, 3):
                xpath = '//*[@id="sameOpe"]'
                choose_url(xpath, 2)
                xpath = '/html/body/div[4]/div/div[2]/div[3]/button[1]'
                choose_url(xpath, 2)
                #print("多个冲突保存文件处理")
            else:
                xpath = '/html/body/div[4]/div/div[2]/div[2]/button[1]'
                choose_url(xpath, 2)
                #print("多个冲突保存文件处理")
    xpath = '/html/body/div[10]/span/div/div/div/span/span'
    wait_xhr_finnish(xpath,10)
    for i in range(10) :
        pointer = chrome.find_element_by_xpath(xpath)
        url_message = pointer.text
        if "操作完成" in url_message:
            update_movie_data(movie_name, "have_episodes", upload_movie_have_episodes)
            print(f'更新完成:{movie_name},当前更新至 {upload_movie_have_episodes} 集')
            return True
        else:
            time.sleep(0.5)
    print(f'错误:转存可能失败')
    return False



def main ():
    #初始化数据库链接
    connect_mysql()
    #获取数据库数据
    grep_data()
    #初始化浏览器
    openchrome()
    #开始更新
    for i in range(movie_num):
        #初始化全局变量，用于后面编写方便
        Initializing_variables(i)
        print(f"\n开始更新:{movie_name}")
        if movie_url_status == 0:
            print(f"错误:当前资源链接已失效,请更新{movie_name}链接")
            continue
        #判断更新间隔,是否更新
        if whether_update_episodes():
            latest_episodes = get_latest_episodes()
        else :
            latest_episodes = movie_latest_episodes
        print(f"当前最新集数:{latest_episodes}")
        # 获取最新集数
        #判断现有的与最新的是否存在差异
        if latest_episodes <= movie_have_episodes :
            print(f"当前文件已是最新的，跳过更新")
            continue
        #判断资源网站决定跑哪个更新程序
        if "cloud.189.cn" in movie_update_url :
            if not update_189cloud() :
                print("更新失败:请排查日志")
                continue
        elif "cloud.quark.cn" in movie_update_url :
            print("错误：暂未支持其他网盘")


def finnish():
    db.close()
    chrome.quit()

def err_quit():
    chrome.quit()
    db.close()
    quit()


main()
finnish()