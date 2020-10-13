# coding=utf-8
import re
import sys
import time
import random
import requests
import threading
from bs4 import BeautifulSoup
from lxml import etree
from fake_useragent import UserAgent

#用户名
name='UserName'
#密码
password='Password'

s=requests.session()
#登录
def login():
	agent=UserAgent().Chrome
	print('使用UA'+agent+'\n')
	header={'User-Agent' : agent}
	s.headers.update(header)
	try:
		res = s.get('http://codeforces.com/enter?back=%2F')
		soup=BeautifulSoup(res.text,'lxml')
		csrf_token=soup.find(attrs={'name' : 'X-Csrf-Token'}).get('content')
		form_data={
			'csrf_token' : csrf_token,
			'action' : 'enter',
			'ftaa' : '',
			'bfaa' : '',
			'handleOrEmail' : name,
			'password' : password,
			'remember' : []
		}
		s.post('http://codeforces.com/enter',data=form_data)
	except Exception as e:
		print('登陆失败',e)
#获取代码
def getcode(a,b) :
	try:
		res=s.get('http://codeforces.com/problemset/submit')
		soup=BeautifulSoup(res.text,'lxml')
		csrf_token=soup.find(attrs={'name' : 'X-Csrf-Token'}).get('content')
		data={
			'csrf_token' : csrf_token,
			'action' : 'setupSubmissionFilter',
			'frameProblemIndex' : b,
			'verdictName' : 'OK',
			'programTypeForInvoker' : 'cpp.g++11',
			'comparisonType' : 'NOT_USED',
			'judgedTestCount' : '',
		}
		s.post('https://codeforces.com/contest/'+a+'/status',data=data)
		res=s.get('https://codeforces.com/contest/'+a+'/status')
		links=re.findall('submission/(.+?)"',res.text)
		if len(links)<=0 :
			return False
		res2=s.get('https://codeforces.com/contest/'+a+'/submission/'+links[0])
		selector=etree.HTML(res2.text)
		out=selector.xpath('//*[@id="program-source-text"]')[0]
	except Exception as e:
		print('题号:',a+b,'获取代码失败')
		print(e)
		exit(0)
	return out.text


def uploadcode(a,b,code) :
	res=s.get('http://codeforces.com/problemset/submit')
	soup=BeautifulSoup(res.text,'lxml')
	csrf_token=soup.find(attrs={'name' : 'X-Csrf-Token'}).get('content')
	post_data={
		'csrf_token' : csrf_token,
		'ftaa' : '',
		'bfaa' : '',
		'action' : 'submitSolutionFormSubmitted',
		'submittedProblemCode' : a+b,
		'programTypeId' : '42',
		'source' : code+'//hello',
		'tabSize' : 0,
		'sourceFile' : '',
	}
	res=s.post('http://codeforces.com/problemset/submit?csrf_token='+csrf_token,data=post_data)
	if res.status_code!=200 :
		print('题号:',a+b,'提交代码失败')
		print(res)
		exit(0)
	else:
		print('题号:',a+b,'AC!!!')


def solve(a) :
	global s
	html=s.get('https://codeforces.com/contest/'+a).text
	if not html :
		return
	links=re.findall('<a href="/contest/'+a+'/problem/(.+?)"><!--',html)
	setlinks=set(links)
	links=list(setlinks)
	links.sort()
	for b in links :
		if len(b)<3 :
			uploadcode(a,b,getcode(a,b))
			jiange=random.randint(600,1800)
			print('下次提交于'+str(jiange)+'s之后\n')
			time.sleep(jiange)
	print('solve:',a)


login()
random.seed(time.time())
from_contest = int(sys.argv[1]) #接受传入参数
for a in range(from_contest,1145):
	threading.Thread(target=solve, args=(str(a),)).start()
	sleep_time=random.randint(14400,86400)
	print('将于'+str(sleep_time)+'秒后进入下一组Contest\n')
	time.sleep(sleep_time)
