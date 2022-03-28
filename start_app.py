

import flask
import json
from utils.json_utils import dump_user_dialogue_context,load_user_dialogue_context

from main_modules import classifier,chat_robot,medical_robot

def QA(msg):
    user_intent=classifier(msg)
    # print(user_intent)
    if user_intent in ["greet","goodbye","deny","isbot"]:
        reply=chat_robot(user_intent)
    elif user_intent =="accept":
        pass
        # reply = load_user_dialogue_context(msg.User['NickName'])
        # reply = reply.get("choice_answer")
    else:
        reply=medical_robot(msg)
        reply=reply.get('replay_answer')
    return reply





if __name__=="__main__":
    app=flask.Flask(__name__)
    @app.route("/main",methods=["GET","POST"])
    def main():
        param=flask.request.get_json()
        text = param['Text']
        result=QA(text)
        return flask.jsonify(result)
        # return "123"
    app.run("0.0.0.0",port=5003,debug=True)