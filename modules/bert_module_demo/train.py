from bert4keras.backend import keras
from bert4keras.optimizers import Adam
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import sequence_padding,DataGenerator
from sklearn.metrics import classification_report

from modules.bert_module_demo.bert_module import build_bert_model
from modules.bert_module_demo.data_analysis import load_data
class_nums = 13
maxlen = 128##文本最大长度
batch_size = 8


config_path= r"/chinese_rbtl3_L-3_H-1024_A-16/bert_config_rbtl3.json"
checkpoint_path=r"F:\medical_knowledge_atlas_Q&A\chinese_rbtl3_L-3_H-1024_A-16\bert_model.ckpt"
dict_path= r"/chinese_rbtl3_L-3_H-1024_A-16/vocab.txt"
tokenizer = Tokenizer(dict_path)##对文本进行预分词
##定义数据生成器，把数据喂给模型训练
class data_generator(DataGenerator):
    def __iter__(self, random=False):
                           # 分隔符的序列         标签序列
        batch_token_ids, batch_segment_ids, batch_labels = [], [], []
        for is_end, (text, label) in self.sample(random):
            token_ids, segment_ids = tokenizer.encode(text, maxlen=maxlen)#[1,3,2,5,9,12,243,0,0,0]##对原始文本进行编码，按照最大长度切割
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
            batch_labels.append([label])
            if len(batch_token_ids) == self.batch_size or is_end:
                # 将序列padding到同一长度，保证每个训练样本的长度是一致的
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                batch_labels = sequence_padding(batch_labels)
                yield [batch_token_ids, batch_segment_ids], batch_labels
                batch_token_ids, batch_segment_ids, batch_labels = [], [], []
if __name__ == '__main__':
    # 加载数据集
    train_data = load_data(r'F:\medical_knowledge_atlas_Q&A\CMID-master\train.csv')
    test_data = load_data(r'F:\medical_knowledge_atlas_Q&A\CMID-master\test.csv')

    # 转换数据集，转化成数据生成器
    train_generator = data_generator(train_data, batch_size)
    test_generator = data_generator(test_data, batch_size)

    model = build_bert_model(config_path,checkpoint_path,class_nums)
    print(model.summary())
    model.compile(##模型编译之后才可训练
        loss='sparse_categorical_crossentropy',#交叉熵损失
        optimizer=Adam(5e-6),#优化器，（学习率）
        metrics=['accuracy'],#训练的评价指标，卷曲率
    )

    earlystop = keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=3,
        verbose=2,
        mode='min'
        )
    bast_model_filepath = '/data/best_model.weights'
    checkpoint = keras.callbacks.ModelCheckpoint(
        bast_model_filepath,
        monitor='val_loss',
        verbose=1,
        save_best_only=True,
        mode='min'
        )

    model.fit_generator(
        train_generator.forfit(),
        steps_per_epoch=len(train_generator),
        epochs=10,
        validation_data=test_generator.forfit(),#验证集用测试集
        validation_steps=len(test_generator),
        shuffle=True,
        callbacks=[earlystop,checkpoint]
    )
    ##加载模型最佳的用来做测试
    model.load_weights(bast_model_filepath)
    test_pred = []
    test_true = []
    for x,y in test_generator:
        p = model.predict(x).argmax(axis=1)
        test_pred.extend(p)

    test_true = test_data[:,1].tolist()
    print(set(test_true))
    print(set(test_pred))

    target_names = [line.strip() for line in open('label', 'r', encoding='utf8')]
    print(classification_report(test_true, test_pred,target_names=target_names))

