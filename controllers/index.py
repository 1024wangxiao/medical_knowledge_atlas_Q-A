import flask
from flask import Blueprint,request,render_template
index_page=Blueprint("index_page",__name__)



@index_page.route("/",methods=["post","GET"])
def hello():
        return  render_template('index.html')
