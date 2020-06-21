from flask import Flask,render_template,request,redirect,url_for,session,flash
import time
import json
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = b'dd06be55a06c03312b2ab109b5f8f6ab'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'


class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(使用者):
	with open('./member.json','r') as file_object:
		users = json.load(file_object)
	if 使用者 not in users:
		return
	user = User()
	user.id = 使用者
	return user

@login_manager.request_loader
def request_loader(request):
	with open('./member.json','r') as file_object:
		users = json.load(file_object)
	使用者 = request.form.get('user_id')
	if 使用者 not in users:
		return

	user = User()
	user.id = 使用者
		
	# DO NOT ever store passwords in plaintext and always compare password
	# hashes using constant-time comparison!
	user.is_authenticated = request.form['password'] == users[使用者]['password']

	return user


@app.route('/',methods=['POST','GET'])
def index():
	if request.method =='POST':
		if request.values['send']=='送出':
			return render_template('index.html',name=request.values['user'])
	return render_template('index.html',name="")


	
@app.route('/login', methods=['GET', 'POST'])
def login():
	with open('./member.json','r') as file_object:
		member = json.load(file_object)
	if request.method == 'GET':
		return render_template("login.html")
	
	使用者 = request.form['user_id']
	if (使用者 in member) and (request.form['password'] == member[使用者]['password']):
		user = User()
		user.id = 使用者
		login_user(user)
		return redirect(url_for('index'))

	flash('登入失敗了...')
	return render_template('login.html')

@app.route('/logout')
def logout():
    使用者 = current_user.get_id()
    logout_user()
    return redirect(url_for('index'))

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
				basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
				os.mkdir(os.path.join(basepath,request.values['userid']))
				return render_template('index.html')
	return render_template('register.html')

@app.route('/upload/',methods=['GET','POST'])
def upload():

	basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
	dirs=os.listdir(os.path.join(basepath,session.get('username')))
	dirs.insert(0,'New Folder')
	dirs.insert(0,'Not Choose')

	if request.method == 'POST':
		flist = request.files.getlist("file[]")
		
		for f in flist:
			try:
				basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
				format=f.filename[f.filename.index('.'):]
				fileName=time.time()
				if format in ('.jpg','.png','.jpeg','.HEIC','.jfif'):
					format='.jpg'
				else:
					format='.mp4'
					

				if request.values['folder']=='0':
					return render_template('upload.html',alert='Please choose a folder or creat a folder',dirs=dirs)

				elif request.values['folder']=='1':
					if not os.path.isdir(os.path.join(basepath,session.get('username'),request.values['foldername'])):
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername']))
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername'],'video'))
						os.mkdir(os.path.join(basepath,session.get('username'),request.values['foldername'],'photo'))
					
					if format == '.mp4':
						upload_path = os.path.join(basepath,session.get('username'),request.values['foldername'],'video',str(fileName).replace('.','')+str(format))
					else:
						upload_path = os.path.join(basepath,session.get('username'),request.values['foldername'],'photo',str(fileName).replace('.','')+str(format))   
				else:
					if format == '.mp4':
						upload_path = os.path.join(basepath,session.get('username'),dirs[int(request.values['folder'])],'video',str(fileName).replace('.','')+str(format))
					else:
						upload_path = os.path.join(basepath,session.get('username'),dirs[int(request.values['folder'])],'photo',str(fileName).replace('.','')+str(format))
				
				
				f.save(upload_path)
			except:
				return render_template('upload.html',alert='你沒有選擇要上傳的檔案',dirs=dirs)

		return redirect(url_for('upload'))
	return render_template('upload.html',dirs=dirs)
	
if __name__ == '__main__':
	app.run(host='0.0.0.0',port='5000',debug=True)
