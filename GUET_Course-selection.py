#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : chainsx
# @FileName: GUET_Course-selection.py
import json
import requests
from aip import AipOcr
import time

APP_ID = 'xxxxx' #百度OCR的APPID
API_KEY = 'xxxx' #百度OCR的AK
SECRET_KEY = 'xxxx' #百度OCR的SK
SERVER_JAM = 'xxxx' #server酱的SCKEY

user = "19003xxxxx"
# 学号
pwd = "xxxxxx"
# WEB_VPN密码
jiaowu_pwd = "xxxxxxx"
# 教务系统密码
header = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Cookie': None,
    'Origin': 'https://v.guet.edu.cn',
    'Referer': None,
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/87.0.4280.141 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    }

url = "https://v.guet.edu.cn/do-login?local_login=true"
# WEB_VPN登录地址
data = {
    'auth_type': 'local',
    'username': user,
    'sms_code': '',
    'password': pwd,
    'remember_cookie': 'on',
    }
# WEB_VPN登录表单
res = requests.post(url, data=data)
# 进行WEB_VPN登录操作
restext = res.text
loginCookieDict = requests.utils.dict_from_cookiejar(res.cookies)
# 获取token，参考hanxven神佬的操作
cookie = {
    'show_vpn': '1',
    'wengine_vpn_ticket': loginCookieDict['wengine_vpn_ticket'],
    'refresh': '0',
    }
# WEB_VPN的cookie
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
# 百度OCR的API
imgurl = "https://v.guet.edu.cn/http/77726476706e69737468656265737421a1a013d2766626012d46dbfe/login" \
         "/GetValidateCode?id=0.19919704308044928 "
# 教务系统验证码地址
new_header = "show_vpn=1; wengine_vpn_ticket=" + str(loginCookieDict['wengine_vpn_ticket']) + "; refresh=1"
header['Cookie'] = new_header
# 别问，老子只是看到header里面包括了cookie就加上去了
r = requests.get(imgurl, headers=header, cookies=cookie)
# 获取验证码图片
with open('img.png', 'wb') as f:
    f.write(r.content)


# 别问为什么要保存图片，问就是百度OCR不支持https还有这是gay电内网
def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


image = get_file_content('img.png')
imgres = client.basicGeneral(image)
# 使用baiduOCR获取验证码，标准图片识别，
# 经过测试，识别成功率存在但是不高。。。。如果失败了多试几次就好了
print(imgres)
codeimg = imgres['words_result']
finalcode = codeimg[0]
# finalcode是百度OCR返回的字典，里面的word对应的value就是识别结果
data_jiaowu = {
    'us': user,
    'pwd': jiaowu_pwd,
    'ck': finalcode['words'],
    }
# 教务系统登录表单
homePage = "https://v.guet.edu.cn/http/77726476706e69737468656265737421a1a013d2766626012d46dbfe/Login/SubmitLogin"
header['Referer'] = 'https://v.guet.edu.cn/http/77726476706e69737468656265737421a1a013d2766626012d46dbfe/'
# 换一下referer
res_home = requests.post(homePage, headers=header, cookies=cookie, data=data_jiaowu)
# 进行登录教务系统操作
home_page_info_dict = json.loads(res_home.text)

print(str(home_page_info_dict))
print(str(home_page_info_dict['msg']))
if str(home_page_info_dict['success']) == 'False':
    quit()

# 输出一下，看一下登录成功没有
header['Referer'] = "https://v.guet.edu.cn/http/77726476706e69737468656265737421a1a013d2766626012d46dbfe/Login" \
                    "/MainDesktop "
limit_dist = {
    '_dc': str(int(time.time() * 1000)),
    'page': '1',
    'start': '0',
    'limit': '25',
    }
# 一些基本操作需要post这个表单来限制服务器下发的信息
# get info
# 获取基本信息
get_term_addr = "https://v.guet.edu.cn/http/77726476706e69737468656265737421a1a013d2766626012d46dbfe/student/StuInfo"
get_term = requests.post(get_term_addr, headers=header, cookies=cookie, data=limit_dist)
termtext = get_term.text
get_term_data = json.loads(termtext)
term = get_term_data['term']  # 当前学期
grade = get_term_data['grade']  # 你tm所在的年级
spno = get_term_data['spno']  # 专业代码
stid = get_term_data['stid']  # 学号
name = get_term_data['name']  # 你的狗名
dptno = get_term_data['dptno']  # 学院代码，比如说：3
print(term, grade, spno, stid, name, dptno)
# 输出一下，有点成就感
# get course info
# 获取你当前还能选择的课程
null = None
# py里面的空是None，想了一个好方法来解决了这个问题
course_dist = {
    '_dc': str(int(time.time() * 1000)),
    'term': term,
    'grade': grade,
    'spno': spno,
    'stype': '正常',
    'page': '1',
    'start': '0',
    'limit': '25',
    }
# 获取课程信息所需要的表单
get_course_addr = "https://v.guet.edu.cn/http/77726476706e69737468656265737421a1a013d2766626012d46dbfe/student/GetPlan"
get_course = requests.post(get_course_addr, headers=header, cookies=cookie, data=course_dist)
# 获取
coursetext = get_course.text
get_course_data_tmp = json.loads(coursetext)
course_data = get_course_data_tmp['data']
courses = len(course_data)
for i in range(courses):
    print(course_data[i]['cname'])
# 挨个打印
# get course info
course_info_dist = {
    '_dc': str(int(time.time() * 1000)),
    'id': None,
    'term': None,
    'courseid': None,
    'cname': None,
    'spno': None,
    'grade': None,
    'tname': None,
    'xf': None,
    'scted': None,
    'page': '1',
    'start': '0',
    'limit': '25',
    'group': '[{"property":"scted","direction":"ASC"}]',
    'sort': '[{"property":"scted","direction":"ASC"}]',
    }

get_course_info_addr = "https://v.guet.edu.cn/http/77726476706e69737468656265737421a1a013d2766626012d46dbfe/student" \
                       "/GetPlanCno"
for i in range(courses):
    course_info_dist['id'] = course_data[i]['id']
    course_info_dist['term'] = course_data[i]['term']
    course_info_dist['courseid'] = course_data[i]['courseid']
    course_info_dist['cname'] = course_data[i]['cname']
    course_info_dist['spno'] = course_data[i]['spno']
    course_info_dist['grade'] = course_data[i]['grade']
    course_info_dist['tname'] = course_data[i]['tname']
    course_info_dist['xf'] = course_data[i]['xf']
    course_info_dist['scted'] = course_data[i]['scted']
    while True:
        get_course_info = requests.get(get_course_info_addr, headers=header, cookies=cookie, data=course_info_dist)
        courseinfotext = get_course_info.text
        course_info_tmp = json.loads(courseinfotext)
        course_info_data = course_info_tmp['data']
        for course_num in range(len(course_info_data)):
            if (course_info_data[course_num]['maxstu'] == course_info_data[course_num]['sctcnt']):
                xuanke_dist = {
                    'term': course_info_data[course_num]['term'],
                    'courseno': course_info_data[course_num]['courseno'],
                    'grade': course_info_data[course_num]['grade'],
                    'spno': course_info_data[course_num]['spno'],
                    'scted': course_info_data[course_num]['scted'],
                    'name': course_info_data[course_num]['name'],
                    'ap': course_info_data[course_num]['ap'],
                    'xf': course_info_data[course_num]['xf'],
                    'lot': course_info_data[course_num]['lot'],
                    'courseid': course_info_data[course_num]['courseid'],
                    'stype': '正常',
                    'maxstu': course_info_data[course_num]['maxstu'],
                    'sctcnt': course_info_data[course_num]['sctcnt'],
                    'comm': course_info_data[course_num]['comm'],
                    'id': course_info_data[course_num]['id'],
                    }
                get_course_addr = "https://v.guet.edu.cn/http" \
                                  "/77726476706e69737468656265737421a1a013d2766626012d46dbfe/student/SctSave"
                print(str(xuanke_dist))
                get_course = requests.post(get_course_addr, headers=header, cookies=cookie, data=json.dumps(xuanke_dist))
                coursetext = get_course.text
                print(coursetext)
                '''
                push_dist = {
                    'text': '选课变动',
                    'desp': coursetext,
                    }
                push_url = 'http://sc.ftqq.com/' + SERVER_JAM + '.send'
                push = requests.get(push_url, params=push_dist)
                '''
            if course_info_data[course_num]['maxstu'] == course_info_data[course_num]['sctcnt']:
                print("full")

        time.sleep(5)
