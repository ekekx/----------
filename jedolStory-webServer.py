# app.py
# from flask import Flask, render_template, request, jsonify
from flask import Flask,request,abort, render_template, send_from_directory,jsonify,redirect, url_for, session, redirect, app
import os
import jedol3AiFun as jedol3AiFun
from datetime import datetime, timedelta
import jedol1Fun as jshs
import jedol2ChatDbFun as chatDB
from file_uploader import upload_file

app = Flask(__name__)

chatDB.setup_db()

app.secret_key = 'jedolstory'

selected_file = ''

@app.errorhandler(404)
def not_found(e):
    return render_template('/html/404.html'), 404



@app.route('/uploader', methods=['POST'])
def uploader():
    result = upload_file()
    return result

@app.route('/', methods=['GET', 'POST'])
def showfiles():
    folder_path = "C:/Users/USER/OneDrive/바탕 화면/문제 제작 프로그램/data"  # data 폴더 경로 설정
    files = os.listdir(folder_path)
    return render_template('/html/show.html', files=files)

@app.route("/chat")
def index():
   global selected_file
   selected_file = request.args.get('selected_file', default='', type=str)
   print(selected_file)
   if not 'token' in session:
        session['token'] = jshs.rnd_str(n=20, type="s")
        print("new-token",session['token'])    
        chatDB.new_user(session['token'])
   else:
        print("old-token",session['token'])
    
   return render_template("/html/index.html",token=session['token'])

@app.route('/<path:page>')

def page(page):
   print(page)
   try:
        if ".html" in page:
            return render_template(page )
        else:
            return send_from_directory("templates", page)
   except Exception as e:
        abort(404)

@app.route("/query", methods=["POST"])
def query():
    global selected_file
    query  = request.json.get("query")
    today = str( datetime.now().date().today())
    vectorDB_folder=f"vectorDB-faiss-jshs-{today}"

    print(selected_file)

    if os.path.exists(vectorDB_folder) and os.path.isdir(vectorDB_folder):
         
         query  = request.json.get("query")
         print( "기존데이터 사용=",vectorDB_folder )
         print( "질문",query )
         answer = jedol3AiFun.ai_reponse(vectorDB_folder, query, session['token'])
    else:
        print( "백터db만들기=", vectorDB_folder )
        
        vectorDB_folder=jedol3AiFun.vectorDB_create(vectorDB_folder, selected_file=selected_file)
        print( "질문",query )
        answer = jedol3AiFun.ai_reponse( vectorDB_folder, query, session['token'])

    return jsonify({"answer": answer })

if __name__ == "__main__":
       app.run(debug=True,host="0.0.0.0",port=5001)

