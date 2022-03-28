import json
import codecs
import threading
from py2neo import Graph
from tqdm import tqdm
def print_data_info(data_path):
    triples = []
    i = 0
    with open(data_path,'r',encoding='utf8') as f:
        for line in f.readlines():
            data = json.loads(line)
            print(json.dumps(data, sort_keys=True, indent=4, separators=(', ', ': '),ensure_ascii=False))
            i += 1
            if i >=5:
                break
    return triples

class MedicalKG(object):
    def __init__(self):
        super(MedicalKG, self).__init__()
        self.graph = Graph("http://localhost:7474", auth=("neo4j", "wangxiao1024"))
        # # 共8类节点
        self.drugs = []  # 药品
        self.recipes = []  # 菜谱
        self.foods = []  # 食物
        self.checks = []  # 检查
        self.departments = []  # 科室
        self.producers = []  # 药企
        self.diseases = []  # 疾病
        self.symptoms = []  # 症状
        self.treats=[] #治疗方案
        self.disease_infos = []  # 疾病信息

        # 构建节点实体关系
        self.rels_department = []  # 科室－科室关系
        self.rels_noteat = []  # 疾病－忌吃食物关系
        self.rels_doeat = []  # 疾病－宜吃食物关系
        self.rels_recommandeat = []  # 疾病－推荐吃食物关系
        self.rels_commonddrug = []  # 疾病－通用药品关系
        self.rels_recommanddrug = []  # 疾病－热门药品关系
        self.rels_check = []  # 疾病－检查关系
        self.rels_drug_producer = []  # 厂商－药物关系
        self.rels_diseases_treat=[] #疾病-治疗关系
        self.rels_symptom = []  # 疾病症状关系
        self.rels_acompany = []  # 疾病并发关系
        self.rels_category = []  # 疾病与科室之间的关系
    def Triplet(self,data_path):
        print("开始提取三元组")
        with open(data_path,"r",encoding="utf-8") as f:
            line_info=f.readlines()
            for line in tqdm(line_info,ncols=80):
                data_json=json.loads(line)
                disease_dict = {}
                disease=data_json['basic_info']['name']
                disease_dict['name']=disease
                self.diseases.append(disease)
                disease_dict['desc'] = ''
                disease_dict['prevent'] = ''
                disease_dict['cause'] = ''
                disease_dict['easy_get'] = ''
                disease_dict['cure_department'] = ''
                disease_dict['get_way'] = ''
                disease_dict['cure_lasttime'] = ''
                disease_dict['symptom'] = ''
                disease_dict['cured_prob'] = ''
                disease_dict['treat']=''
                if 'symptom_info' in data_json:
                    disease_dict['symptom']=data_json['symptom_info']
                    self.symptoms.append(data_json['symptom_info'])
                    self.rels_symptom.append([disease,"has_symptom",data_json['symptom_info']])
                if "并发症" in data_json['basic_info']:
                    disease_acompany=data_json['basic_info']["并发症"].split(' ')
                    for i in disease_acompany:
                        self.diseases.append(i)
                    # self.diseases.append(i for i in (data_json['basic_info']["并发症"]).split(' '))
                        self.rels_acompany.append([disease,"acompany_with",i])
                # # print(self.diseases)
                # print(self.rels_acompany)
                if 'desc' in data_json['basic_info']:
                    disease_dict['desc']=data_json['basic_info']["desc"]
                # print(disease_dict['desc'])
                if "prevent_info" in data_json:
                    disease_dict['prevent']=data_json['prevent_info']
                if "cause_info" in data_json:
                    disease_dict['cause']=data_json['cause_info']
                if "患病比例" in data_json['basic_info']:
                    disease_dict["easy_get"]=data_json['basic_info']["患病比例"]
                if "易感人群" in data_json['basic_info']:
                    disease_dict['easy_get']=data_json['basic_info']['易感人群']
                if '就诊科室' in data_json['basic_info']:
                    department=data_json['basic_info']['就诊科室'].rstrip().split("  ")
                    # print(department)
                    if len(department)==1:
                        self.rels_category.append([disease,"cure_department",department[0]])
                    if len(department)==2:
                        big = department[0]
                        small = department[1]
                        self.rels_department.append([small,"belong_to",big])
                        self.rels_category.append([disease,"cure_department",small])
                    disease_dict['cure_department']=department
                    for data in department:
                        self.departments.append(data)
                    # print(self.departments)
                    # print(self.rels_department)
                    # print(self.rels_category)
                if "传染方式" in data_json['basic_info']:
                    disease_dict['cure_way']=data_json['basic_info']["传染方式"]
                if "治疗周期" in data_json['basic_info']:
                    disease_dict['cure_lasttime']=data_json['basic_info']["治疗周期"]
                if "治愈率" in data_json['basic_info']:
                    disease_dict['cured_prob']=data_json['basic_info']['治愈率']
                if " 常用药品" in data_json['basic_info']:
                    common_drug = data_json['basic_info'][" 常用药品"].split(" ")
                    for drug in common_drug:
                        if drug:
                            self.rels_commonddrug.append([disease,"has_common_drug",drug])
                            self.drugs.append(drug)
            # print(self.rels_commonddrug)
                if 'food_info' in data_json :
                    recommand_eat=data_json['food_info']['good_cooking_reconmand']
                    self.rels_recommandeat.append([disease,"recommand_eat",recommand_eat])
                    self.recipes.append(recommand_eat)
                    if "bad_eat" in data_json['food_info'] :
                        not_eat=data_json['food_info']['bad_eat'].split(',')
                        for eat_not in not_eat:
                            self.rels_noteat.append([disease,"not_eat",eat_not])
                            self.foods.append(eat_not)
                    if 'good_eat' in data_json['food_info']:
                        good_eat=data_json['food_info']['good_eat'].split(',')
                        for eat_good in good_eat:
                            self.rels_doeat.append([disease,"do_eat",eat_good])
                            self.foods.append(eat_good)
                    # print(self.foods)
                    # print(self.rels_recommandeat)
                    # print(self.recipes)
                    # print(self.rels_noteat)
                    # print(self.rels_doeat)
                if "inspect_info" in data_json:
                    check=data_json['inspect_info']
                    self.rels_check.append([disease,"need_check",check])
                    self.checks.append(check)
                    # print(self.rels_check)
                    # print(self.checks)

                if "drug_info" in data_json:
                    for drug_det in data_json['drug_info']:
                        drug_det =drug_det.split('(')
                        if len(drug_det) ==2:
                            start,end=drug_det
                            end=end.rstrip(')')
                            if start.find(end):
                                start=start.rstrip(end)
                            self.producers.append(start)
                            self.drugs.append(end)
                            self.rels_recommanddrug.append([disease,"recommand_drug",end])
                            self.rels_drug_producer.append([start,'production',end])
                        else:
                            end=drug_det[0]
                            self.drugs.append(end)
                        # print(self.rels_recommanddrug)
                    # print(self.drugs)
                    # print((self.producers))
                    # print(self.rels_drug_producer)
                if "treat_info" in data_json:
                    treat=data_json['treat_info']
                    disease_dict['treat']=treat
                    self.treats.append(treat)
                    self.rels_diseases_treat.append([disease,"has_treat",treat])
                    # print(self.treats)
                    # print(self.rels_diseases_treat)
                self.disease_infos.append(disease_dict)
    def write_nodes(self,entitys,entity_type):
        print("开始写入{0} 实体".format(entity_type))
        # count=0
        for node in tqdm(set(entitys),ncols=80):
            if node!="":
            # print(node)
                cql = """MERGE(n:{label}{{name:'{entity_name}'}})""".format(
                    label=entity_type, entity_name=node.replace("'", ""))
                # print(cql)
                # count+=1

                try:
                    self.graph.run(cql)
                except Exception as e:
                    print(cql,e)

        # print(count)
    def write_edges(self,triples,head_type,tail_type):
        # print(triples)
        print("开始写入 {0} 关系".format(triples[0][1]))
        for head,relation,tail in tqdm(triples,ncols=80):
            cql = """MATCH(p:{head_type}),(q:{tail_type})
                    WHERE p.name='{head}' AND q.name='{tail}'
                    MERGE (p)-[r:{relation}]->(q)""".format(
                        head_type=head_type,tail_type=tail_type,head=head.replace("'",""),
                        tail=tail.replace("'",""),relation=relation)
            try:
                self.graph.run(cql)
            except Exception as e:
                print(e)
                print(cql)
    def set_attributes(self,entity_infos,etype):
        print("写入 {0} 实体的属性".format(etype))
        # count=0
        for e_dict in tqdm(entity_infos, ncols=80):
            if e_dict["name"]:
                # print(e_dict)
                name = e_dict['name']
                del e_dict['name']
                # print(e_dict)
                for key, value in e_dict.items():
                    # print(key)
                    # print(value)
                    if key =='cure_department':
                        cql = """MATCH (n:{label})
                                WHERE n.name='{name}'
                                set n.{key}={value}""".format(label=etype,name=name.replace("'", ""), key=key, value=value)
                    else:
                        cql = """MATCH (n:{label})
                                WHERE n.name='{name}'
                                set n.{key}='{value}'""".format(label=etype, name=name.replace("'",""), key=key,
                                                                                value=value.replace("'",""))
                    # print(cql)
                        try:
                            self.graph.run(cql)
                        except Exception as e:
                            print(e)
                            print(cql)

    def creat_entitys(self):
        self.write_nodes(self.drugs, '药品')
        self.write_nodes(self.recipes, '菜谱')
        self.write_nodes(self.foods, '食物')
        self.write_nodes(self.checks, '检查')
        self.write_nodes(self.departments, '科室')
        self.write_nodes(self.producers, '药企')
        self.write_nodes(self.diseases, '疾病')
        self.write_nodes(self.symptoms, '症状')
        self.write_nodes(self.treats,"治疗方案")
    def create_relations(self):
        self.write_edges(self.rels_department, '科室', '科室')
        self.write_edges(self.rels_noteat, '疾病', '食物')
        self.write_edges(self.rels_doeat, '疾病', '食物')
        self.write_edges(self.rels_recommandeat, '疾病', '菜谱')
        self.write_edges(self.rels_commonddrug, '疾病', '药品')
        self.write_edges(self.rels_recommanddrug, '疾病', '药品')
        self.write_edges(self.rels_check, '疾病', '检查')
        self.write_edges(self.rels_drug_producer, '药企', '药品')
        self.write_edges(self.rels_symptom, '疾病', '症状')
        self.write_edges(self.rels_acompany, '疾病', '疾病')
        self.write_edges(self.rels_category, '疾病', '科室')
        self.write_edges(self.rels_diseases_treat,'疾病','治疗方案')
    def set_diseases_attributes(self):
        # self.set_attributes(self.disease_infos,"疾病")
        t=threading.Thread(target=self.set_attributes,args=(self.disease_infos,"疾病"))
        t.setDaemon(False)
        t.start()



if __name__=='__main__':
    path='../data/medical_care.json'
    medicalkg=MedicalKG()
    medicalkg.Triplet(path)#提取三元组
    # medicalkg.creat_entitys()#导入实体
    # medicalkg.create_relations()#导入关系
    medicalkg.set_diseases_attributes()#导入属性
    # print_data_info("../data/medical_care.json")
