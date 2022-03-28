import random
from py2neo import Graph
import requests
import json
from config import *
from modules.LR_GBDT.clf_model import CLFModel
LR_GBDT=CLFModel('./modules/LR_GBDT/model_weights/')
graph = Graph("http://localhost:7474", auth=("neo4j", "wangxiao1024"))





def intent_classifier(text):
    url = 'http://192.168.31.112:5002/service/api/bert'
    data = {"text":text}
    # print(data)
    headers = {'Content-Type':'application/json;charset=utf8'}
    reponse = requests.post(url,data=json.dumps(data),headers=headers)
    if reponse.status_code == 200:
        reponse = json.loads(reponse.text)
        # print(reponse)
        return reponse['data']
    else:
        return -1
def slot_recognizer(text):
    url = 'http://192.168.31.112:5001/service/api/ner'
    data = {"text_list":text}
    headers = {'Content-Type':'application/json;charset=utf8'}
    reponse = requests.post(url,data=json.dumps(data),headers=headers)
    if reponse.status_code == 200:
        reponse = json.loads(reponse.text)
        return reponse['data']
    else:
        return -1

def classifier(msg):
    ##对用户初次意图进行判断分为：
    """
    greet,goodbye,deny,isbot

    """
    return LR_GBDT.predict(msg)

def entity_link(mention,etype):
    """
    对于识别到的实体mention,如果其不是知识库中的标准称谓
    则对其进行实体链指，将其指向一个唯一实体（待实现）
    """
    return mention

def text_analysis(msg):
    """
    文本解析
    :param msg:
    :return:
    """
    intent_msg=intent_classifier(msg)
    entity=slot_recognizer(msg)
    # print(intent_msg)
    # print(entity)

    if intent_msg.get("name")=='其他'or intent_msg==-1 or entity==-1:
        return semantic_slot.get("unrecognized")
    slot_info=semantic_slot.get(intent_msg.get('name'))

    ##语义槽的填充
    slots=slot_info.get('slot_list')#Disease
    slot_values={}
    for slot in slots:
        slot_values[slot]=None
        for ent_info in entity:
            for e in ent_info["entities"]:
                if slot.lower() ==e['type']:
                    slot_values[slot]=entity_link(e['word'],e['type'])##做实体链接把实体传到字典里面
    slot_info['slot_values']=slot_values
    # print(slot_values)
    # print(slot_info)
    conf=intent_msg.get('confidence')
    # print(slot_info)
    if conf >= intent_threshold_config["accept"]:
        slot_info["intent_strategy"] = "accept"
    elif conf >= intent_threshold_config["deny"]:
        slot_info["intent_strategy"] = "clarify"
    else:
        slot_info["intent_strategy"] = "deny"

    return slot_info


def neo4j_searcher(cql_list):
    ress = ""
    if isinstance(cql_list, list):
        for cql in cql_list:
            rst = []
            data = graph.run(cql).data()
            if not data:
                continue
            for d in data:
                d = list(d.values())
                if isinstance(d[0], list):
                    rst.extend(d[0])
                else:
                    rst.extend(d)

            data = "、".join([str(i) for i in rst])
            ress += data + "\n"
    else:
        data = graph.run(cql_list).data()
        if not data:
            return ress
        rst = []
        for d in data:
            d = list(d.values())
            if isinstance(d[0], list):
                rst.extend(d[0])
            else:
                rst.extend(d)

        data = "、".join([str(i) for i in rst])
        ress += data

    return ress

def get_answer(slot_info):
    """
    根据语义槽获取答案回复
    """
    cql_template = slot_info.get("cql_template")
    reply_template = slot_info.get("reply_template")
    ask_template = slot_info.get("ask_template")
    slot_values = slot_info.get("slot_values")
    strategy = slot_info.get("intent_strategy")

    if not slot_values:
        return slot_info

    if strategy == "accept":
        cql = []
        if isinstance(cql_template, list):
            for cqlt in cql_template:
                # print(cqlt)
                cql.append(cqlt.format(**slot_values))
        else:
            cql = cql_template.format(**slot_values)
        print(cql)
        answer = neo4j_searcher(cql)
        if not answer:
            slot_info["replay_answer"] = "唔~我装满知识的大脑此刻很贫瘠"
        else:
            pattern = reply_template.format(**slot_values)
            slot_info["replay_answer"] = pattern + answer
    elif strategy == "clarify":
        # 澄清用户是否问该问题
        pattern = ask_template.format(**slot_values)
        slot_info["replay_answer"] = pattern
        # 得到肯定意图之后需要给用户回复的答案
        cql = []
        if isinstance(cql_template, list):
            for cqlt in cql_template:
                cql.append(cqlt.format(**slot_values))
        else:
            cql = cql_template.format(**slot_values)
        answer = neo4j_searcher(cql)
        if not answer:
            slot_info["replay_answer"] = "唔~我装满知识的大脑此刻很贫瘠"
        else:
            pattern = reply_template.format(**slot_values)
            slot_info["choice_answer"] = pattern + answer
    elif strategy == "deny":
        slot_info["replay_answer"] = slot_info.get("deny_response")

    return slot_info


def chat_robot(intent):
    """
    闲聊机器人
    :param intent:
    :return: 根据意图随机返回一条自定义模板中的回复。
    """
    return random.choice(cheat_corpus.get(intent))


def medical_robot(msg):
    """
    医疗机器人
    :param msg:
    :return:
    """
    semantic_slot=text_analysis(msg)
    # print(semantic_slot)
    answer=get_answer(semantic_slot)
    return answer
    # return "ok"

# if __name__=='__main__':
#     medical_robot("你好我感冒了,应该吃什么药")