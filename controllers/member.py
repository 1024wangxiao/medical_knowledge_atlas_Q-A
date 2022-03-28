from flask import Blueprint, render_template, request, jsonify,make_response,session,g
import flask
from application import app
from main_modules import classifier,chat_robot,medical_robot
member_page=Blueprint('member_page',__name__)
from common.libs.Helper import ops_renderJSON,ops_renderErrJSON
from common.libs.UserService import UserService
from utils.json_utils import *

@member_page.route('/QA',methods=["post","GET"])
def QA():
    if request.method=='GET':
        return  render_template('member/qa.html')
    # resp=make_response()
    # resp.delete_cookie('USERNAME')
    # resp.delete_cookie('REPLY')
    # req=request.values
    # question=req['Text'] if "Text" in req else ""
    # username=req['Username'] if "Username" in req else ""
    # if username is None or len(question)<1:
    #     return  ops_renderErrJSON(msg='请输入您的姓名，然后再使用问答功能')
    # if question is None or len(question)<1:
    #     return  ops_renderErrJSON(msg='请输入您想要询问的问题，然后再按确定')
    #
    # # return  ops_renderJSON(msg="询问成功")
    #
    # user_intent = classifier(question)
    # print(user_intent)
    # if user_intent in ["greet", "goodbye", "deny", "isbot"]:
    #     reply = chat_robot(user_intent)
    # elif user_intent == "accept":
    #     # pass
    #     reply = load_user_dialogue_context(username)
    #     reply = reply.get("choice_answer")
    # else:
    #     reply = medical_robot(question)
    #     if reply["slot_values"]:
    #         dump_user_dialogue_context(username,reply)
    #     reply = reply.get('replay_answer')
    # print(reply)
    # session['reply']=reply
    # session['username']=username
    # print(reply)
    # print(type(reply))
    # response=make_response(ops_renderJSON(msg="查询成功"))
    # response.set_cookie(app.config['USER_LOG'],username)
    # response.set_cookie(app.config['USER_REPLY'],reply)
    # g.user=request.cookies['REPLY']
    # print(g.user)
    # return ops_renderJSON(msg="询问成功",data=reply)

@member_page.route('/visual',methods=["post","GET"])
def visual():
    return  render_template('member/visual.html')

@member_page.route('/analysis',methods=["post","GET"])
def analysis():
    # if request.method=='GET':
    #     return render_template('member/answer.html')
    # # data={}
    # # data['username']=request.cookies['USERNAME']
    # # data['REPLY']=request.cookies['REPLY']
    # req=request.values
    # print(req)
    # return ops_renderJSON(msg="查询成果")
    req=request.values
    question=req['Text'] if "Text" in req else ""
    username=req['Username'] if "Username" in req else ""
    if username is None or len(question)<1:
        return  ops_renderErrJSON(msg='请输入您的姓名，然后再使用问答功能')
    if question is None or len(question)<1:
        return  ops_renderErrJSON(msg='请输入您想要询问的问题，然后再按确定')

    # return  ops_renderJSON(msg="询问成功")

    user_intent = classifier(question)
    print(user_intent)
    if user_intent in ["greet", "goodbye", "deny", "isbot"]:
        reply = chat_robot(user_intent)
    elif user_intent == "accept":
        # pass
        reply = load_user_dialogue_context(username)
        reply = reply.get("choice_answer")
    else:
        reply = medical_robot(question)
        if reply["slot_values"]:
            dump_user_dialogue_context(username,reply)
        reply = reply.get('replay_answer')
    print(reply)
    return ops_renderJSON(msg="查询成功",data=reply)

