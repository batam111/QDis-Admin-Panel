from firebase import firebase
import os
import json
import pyrebase
from firebase_admin import credentials, auth,db
from flask import Flask, render_template,request,session
from requests import post
from functools import wraps
global global_token

user_table_heading = ["Full Name", "Username",  "Publisher Status","Date of Birth","Biography","Delete User","Mute User"]
userPosts_table_heading= ["User Id","Category","postId","Username","Content","Title"]
hashtag_table_heading = ["Hash tag" ,"Number of mentions","Remove Hashtag" ]
#data = [["Alex","Alex123","Wow biography","Publisher","123456"]]
file_path1 = os.path.join(os.path.dirname(os.path.abspath(__file__)),"fbAdminConfig.json")
file_path2 = os.path.join(os.path.dirname(os.path.abspath(__file__)),"fbconfig.json")
app = Flask(__name__)
app.secret_key = "super secret key123"
firebase1 = firebase.FirebaseApplication('https://quthisadminpanel-default-rtdb.firebaseio.com/', None)


# Real time Database
credRealTime = credentials.Certificate("realtimeKey.json")
firebase_admin.initialize_app(credRealTime, {
    'databaseURL': 'https://tiktokforsmarties-default-rtdb.firebaseio.com/'
})
firebaseRealTimeDatabase = firebase.FirebaseApplication('https://tiktokforsmarties-default-rtdb.firebaseio.com/', None)
# Real time database -
cred = credentials.Certificate(file_path2)
firebase = firebase_admin.initialize_app(cred,name="auth")
pb = pyrebase.initialize_app(json.load(open(file_path1)))
def check_token():
    try:     
        auth.verify_id_token(session['token'],firebase)
    except KeyError:
        return False
    else:
        return True          
          #  user = auth.verify_id_token(global_token)        
@app.route('/login',methods=["POST","GET"])
def login():       
        username=""
        password1=""
        if request.method=="POST":
            username = request.form["username"]
            password1 = request.form["password"]
            try:
                user = pb.auth().sign_in_with_email_and_password(username,password1)
                session['token'] = user['idToken']
                return render_template("table_template.html") 
            except:  
                return render_template('login.html', incorrect_login_details="True")         
        else:
            return render_template("login.html",incorrect_login_details="False")

def arrange_data_for_html_table(table_name):
    if table_name=='users':
        users = firebaseRealTimeDatabase.get('/users',None)
        arranged_users_data=[]
        single_user_data = []
        for user in users:
            single_user_data = [user,users[user]['fullName'],users[user]['userName'],users[user]['publisher'],users[user]['dob'],users[user]['biography'],users[user]['isMuted']]
            arranged_users_data.append(single_user_data)
        return arranged_users_data
    elif table_name=='usersPosts':
        arranged_post_data=[]
        single_post_data = []
        posts_ref = db.reference('/userPosts').get()
        for userKey , val in posts_ref.items():                       
            for category , val_ in val.items():              
                for postId, val__ in val_.items():
                    single_post_data.append(userKey) 
                    single_post_data.append(userKey)    
                    single_post_data.append(category)                                     
                    single_post_data.append(postId)
                    for postData , val___ in val__.items():
                       if postData == 'author' or postData =='postContent' or postData=='title':
                            single_post_data.append(val___)
                    arranged_post_data.append(single_post_data)
                    single_post_data=[]                      
        return arranged_post_data
    elif table_name == 'hashTags':
        arranged_data=[]
        single_data = []
        hashtag_ref = db.reference('/hashTags').get()
        for hashtagName,value in hashtag_ref.items():
            single_data = (["",hashtagName,len(value)])
            arranged_data.append(single_data) 
        return arranged_data

       
@app.route('/users',methods=['GET','POST'])
def users():
    if not check_token():
        return "Unauthorized access"
    if request.method=="POST" and request.form.get('action') =='Delete': # Delete user action
        user_key_to_delete = request.form.get('userKey')
        user_ref_to_delete = db.reference('users/'+user_key_to_delete).get()
        if(user_ref_to_delete):
            db.reference('users/'+user_key_to_delete).delete()
    elif request.method=="POST" and (request.form.get('action') =='Mute' or request.form.get('action') =='Unmute') :
        user_key_to_mute = request.form.get('userKey')
        if  not db.reference('users/'+user_key_to_mute+'/isMuted').get(): # If user is not already muted
            user_key_to_mute = db.reference('users/'+user_key_to_mute+'/isMuted').set(True)  # Mute him
        else: # If user is muted
             user_key_to_mute = db.reference('users/'+user_key_to_mute+'/isMuted').set(False) # Umnute
    table_data = arrange_data_for_html_table("users")      
    return render_template("table_template.html",headings=user_table_heading,data=table_data,table_name="users")

@app.route('/userPosts',methods=['GET','POST'])
def userPosts():
    if not check_token():
        return "Unauthorized access"
    if request.method=="POST": # Delete post action
        user_key_to_delete = request.form.get('userKey')
        postId = request.form.get('postId')
        postCategory = request.form.get('categoryName')
        post_ref_to_delete = db.reference('userPosts/'+user_key_to_delete+"/"+postCategory+"/"+postId).get()
        if(post_ref_to_delete):
            db.reference('userPosts/'+user_key_to_delete+"/"+postCategory+"/"+postId).delete()
    table_data = arrange_data_for_html_table("usersPosts")
    return render_template("table_template.html",headings=userPosts_table_heading,data=table_data,table_name="userPosts")

@app.route('/hashTags',methods=['GET','POST'])
def hashTags():
    if not check_token():
        return "Unauthorized access"
    if request.method=="POST": # Delete post action
        user_key_to_delete = request.form.get('hashTag')
        post_ref_to_delete = db.reference('hashTags/'+user_key_to_delete).get()
        if(post_ref_to_delete):
            db.reference('hashTags/'+user_key_to_delete).delete()
    table_data = arrange_data_for_html_table("hashTags")
    return render_template("table_template.html",headings=hashtag_table_heading,data=table_data,table_name="hashTags")

@app.route('/',methods=['GET','POST'])
def home():
        if request.method=="POST":
            session.pop("token")           
            return render_template("homepage.html")  
        return render_template("homepage.html")  

if __name__== '__main__':
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()
