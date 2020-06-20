from flask import Flask,render_template,request,redirect,url_for
from flask import session
import json
app=Flask(__name__)
app.secret_key= b'ajsdjdijoedsdcde'

@app.route('/',methods=['POST','GET'])
def index():
	if request.method =='POST':
		if request.values['send']=='送出':
			return render_template('index.html',name=request.values['user'])
	return render_template('index.html',name="")


@app.route('/register',methods=['POST','GET'])
def register():
	with open('./member.json','r') as file_object:
		member = json.load(file_object)
	if request.method=='POST':
		if request.values['send']=='送出':
			if request.values['userid'] in member:
				for find in member:
					if member[find]['nick']==request.values['username']:
						return render_template('register.html',alert='this account and nickname are used.')
				return render_template('register.html',alert='this account is used.',nick=request.values['username'])
			else:
				for find in member:
					if member[find]['nick']==request.values['username']:
						return render_template('register.html',alert='this nickname are used.',id=request.values['userid'],pw=request.values['userpw'])
				member[request.values['userid']]={'password':request.values['userpw'],'nick':request.values['username']}
				with open('./member.json','w') as f:
					json.dump(member, f)
				return render_template('index.html')
	return render_template('register.html')
	
@app.route('/login',methods=['GET','POST'])
def login():

	if request.method== 'POST' :
		with open('./member.json','r') as file_object:
			member = json.load(file_object)

		if request.values['userid'] in member:
			if member[request.values['userid']]['password']==request.values['userpw']:
				session['username']=request.values['userid']
				return redirect ( url_for ( 'index' ))
			else:
				return render_template('login.html',alert="Your password is wrong, please check again!")
		else:
			return render_template('login.html',alert="Your account is unregistered.")
	return render_template('login.html')


@app.route('/logout',methods=['GET','POST'])
def logout ():
	if request.method=='POST':
		if request.values['send']=='確定':
			session.pop('username',None)
		return redirect(url_for('index'))
	return render_template('logout.html')

if __name__ == '__main__':
	app.run(host='0.0.0.0',port='5000',debug=True)