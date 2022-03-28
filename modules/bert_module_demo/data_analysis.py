import json
import pandas as pd


def gen_tranining_data(raw_data_path):
    label_list=[line.strip() for line in open('/modules/bert_module_demo/label', 'r', encoding="utf-8")]
    # print(label_list)
    label2id={label:idx for idx ,label in enumerate(label_list)}
    # print(label2id)
    data=[]
    with open('../../CMID-master/CMID.json', 'r', encoding='utf-8') as f:
        origin_data=f.read()
        # print(origin_data)
        origin_data=eval(origin_data)
        # print(origin_data)
    label_set=set()
    for item in origin_data:
        text=item['originalText']
        label_class=item['label_4class'][0].strip("'")
        if label_class=="其他":
            data.append([text,label_class,label2id[label_class]])
            continue
        label_class=item['label_36class'][0].strip("'")
        label_set.add(label_class)
        if label_class not in label_list:
            continue
        data.append([text,label_class,label2id[label_class]])
    print(label_set)
    data=pd.DataFrame(data,columns=['text','label_class','label'])
    print(data['label_class'].value_counts())
    data["text_len"]=data['text'].map(lambda  x: len(x))
    print(data['text_len'].describe())
    import matplotlib.pyplot as plt
    plt.hist(data['text_len'],bins=30,rwidth=0.9,density=True)
    plt.show()
    del data['text_len']
    data =data.sample(frac=1.0)
    train_num=int(0.9*len(data))
    train,test=data[:train_num],data[train_num:]
    train.to_csv('train.csv',index=False)
    test.to_csv('test.csv',index=False)
def load_data(filename):
    #加载数据集
    df=pd.read_csv(filename,header=0)
    return df[['text','label']].values



if __name__=="__main__":
    data_path= "/CMID-master/CMID.json"
    gen_tranining_data(data_path)
