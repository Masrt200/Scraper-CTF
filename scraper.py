from requests import Session,cookies
from bs4 import BeautifulSoup as bs
import json
import threading
import subprocess
import re
import os,sys
import pickle
from progress.bar import ShadyBar

import argparse 

def connect(url):
	if os.path.exists(".cache") and not args.dynamic_login:
		cj=cookies.RequestsCookieJar()
		with open(".cache","rb") as f:
			cook=pickle.load(f)
		cj._cookies=cook
		s=Session()
		s.cookies=cj
		return s
	elif not os.path.exists(".cache") and not args.dynamic_login:
		print(lc+".cache missing! create a new session!!"+rt)
		sys.exit()
	else:
		with Session() as s:
			print(lc+bd+"Connecting...\r"+rt,end='')
			
			try:
				site = s.get(url+'/login')
			except:
				print(og+bd+"Failed to establish a new connection! Name or service not known"+rt)
				sys.exit()
			
			bs_content = bs(site.content, "html.parser")
			token = bs_content.find("input", {"name":"nonce"})["value"]
			login_data = {"name":username,"password":password, "nonce":token}
			resp=s.post(url+'/login',login_data)

			if b'Your username or password is incorrect' in resp.content:
				print(og+bd+"your username or password is incorrect!!"+rt)
				sys.exit()

			print(lc+bd+"\x1b[2KConnected!!"+rt)
			
			with open(".cache",'wb') as f:
				pickle.dump(s.cookies._cookies,f)

			return s

def scrape_challs(s,limit,no):
	for i in range(limit*no,limit*(no+1)):
		try:
			chall_url=url+'/api/v1/challenges/'+str(i)
			result=json.loads(s.get(chall_url).text)

			assert 'success' in result
			attr={'id','name','value','description','category','tags','hints','files'}
			chall_data={}
			for i in attr:
				chall_data[i]=result['data'][i]

			local(chall_data)
		except:
			pass
		bar.next()

def local(exd):
	if exd['hints']==[]: exd['hints']='None'
	master_path=open(".path").read()

	if not os.path.exists(master_path+"./{}".format(exd['category'])):
		pathe(master_path+"./{}".format(exd['category']))
		#process=subprocess.Popen(["mkdir","./{}".format(exd['category'])], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		#process.communicate()

	template="# {}\n\n### Points: {}\n\n### Desciption:\n{}\n\n>Hints: {}\n\n#### tags: {}".format(exd['name'],exd['value'],exd['description'],exd['hints'],exd['tags'])
	path=master_path+"./{}/{}/".format(exd['category'],exd['name'].replace(' ','_'))
	
	pathe(path)
	#process=subprocess.Popen(["mkdir",path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	#process.communicate()

	with open(path+"description.md",'w') as f:
		f.write(template)
	f.close()

	if exd['files'] !=[] and exd['category']=='Forensics':
		for i in exd['files']:
			file=url+i
			filename=re.findall(r'/(.*)\?token',file)[0].split('/')[-1]
			process=subprocess.Popen(["curl",file,"-o",path+filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			process.communicate()

def pathe(path):
	process=subprocess.Popen(["mkdir",path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	process.communicate()


class SolverThread(threading.Thread):
	def run(self):
		thread_number = int(threading.currentThread().getName())
		scrape_challs(s,100//threads,thread_number)



def initialize_parser():
	
	parser=argparse.ArgumentParser(description="Capturing the Scrapes")
	#parser.add_argument('--creds','-c',help="use default creds",action="store_true")
	parser.add_argument('--update','-p',help="if the website updates, use this",action="store_true")
	#parser.add_argument('--cache','-c',help="use stored cache to extract data",action="store_true")
	parser.add_argument('--dynamic_login','-d',help="create a new session for a ctf",action="store_true")
	parser.add_argument('--threads','-t',help="number of threads to use (default -> 8)",type=str)
	#parser.add_argument('--CTFS','--ctfs','-C',help="displays the upcoming CTFS for you to choose from",action="store_true")
	return parser

def main():
	thread=[]
	for i in range(threads):
		string=SolverThread(name = "{}".format(i))
		string.start()
		thread.append(string)
	for i in thread:
		i.join()

#defaults
username="Masrt"
password="12345678"
url="https://ctf.csivit.com"

threads=8
#url=''
lg='\033[92m'
rt='\033[0m'
lr='\033[91m'
lc='\033[96m'
pk='\033[95m'
bd='\033[01m'
og='\033[33m'

parser=initialize_parser()
args=parser.parse_args()

if args.dynamic_login:
	username=input(lg+"@username: "+rt)
	password=input(lg+"@password: "+rt)
	url=input(lg+"@url: "+rt).rstrip('/')
	master_path=input(lg+"@scrape to? (relative path): "+rt)+"/"
	f=open(".path","w").write(master_path)
	if not os.path.exists("master_path"):
		pathe(master_path)


if args.threads !=None:
	threads=int(args.threads)
#elif args.cache:

s=connect(url)
bar = ShadyBar(pk+bd+'Scraping Data'+rt,fill=lg+">"+rt,suffix=lc+'%(percent)d%% - %(elapsed)ds'+rt,max=100//threads*threads)

main()
print(lr+"\nFinished!"+rt)


#choice
#where to save