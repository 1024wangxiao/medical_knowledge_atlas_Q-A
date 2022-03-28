from bert4keras.backend import keras, set_gelu
from bert4keras.models import build_transformer_model
from bert4keras.optimizers import Adam #优化器

set_gelu('tanh')


def textcnn(inputs, kernel_initializer):
    # 3,4,5
    cnn1 = keras.layers.Conv1D( ##一维卷积来提取特征
        256,##feather map cnn的每个卷积层 数据都是以三维形式存在的，多个二维图谱叠在一起，每一个称为一个feature map
        3,#卷积核的大小，覆盖三个大小的token
        strides=1,##步幅
        padding='same',##输出的纬度和输入的纬度是相同的
        activation='relu',
        kernel_initializer=kernel_initializer
    )(inputs)  # shape=[batch_size,maxlen-2,256]
    cnn1 = keras.layers.GlobalMaxPooling1D()(cnn1)  # shape=[batch_size,256]  全局最大池化操作

    cnn2 = keras.layers.Conv1D(
        256,
        4,
        strides=1,
        padding='same',
        activation='relu',
        kernel_initializer=kernel_initializer
    )(inputs)
    cnn2 = keras.layers.GlobalMaxPooling1D()(cnn2)

    cnn3 = keras.layers.Conv1D(
        256,
        5,
        strides=1,
        padding='same',
        kernel_initializer=kernel_initializer
    )(inputs)
    cnn3 = keras.layers.GlobalMaxPooling1D()(cnn3)

    output = keras.layers.concatenate(
        [cnn1, cnn2, cnn3],
        axis=-1)
    output = keras.layers.Dropout(0.2)(output)##解决过拟合问题
    return output


def build_bert_model(config_path, checkpoint_path, class_nums):
    """

    :param config_path: 配置文件路径
    :param checkpoint_path:预训练文件路径
    :param class_nums:分类数量
    :return:
    """
    bert = build_transformer_model(
        config_path=config_path,
        checkpoint_path=checkpoint_path,
        model='bert',#模型种类的选择其中有：（bert、albert、albert_unshared、nezha、electra、gpt2_ml、t5）
                                   ##application='', 模型的用途（encoder、lm、unilm）
        return_keras_model=False)# 返回Keras模型，还是返回bert4keras的模型类

    cls_features = keras.layers.Lambda(#拿到cls（所有行的第一列）
        lambda x: x[:, 0],#所有行的第0列
        name='cls-token'
    )(bert.model.output)  # shape=[batch_size,768]
    ##如果后续不接textcnn的话就可以直接拿到这个token去做识别了
    all_token_embedding = keras.layers.Lambda(#拿到除了cls和结尾seq之外的token，可以看成input经过enbeding之后的情况
        lambda x: x[:, 1:-1],
        name='all-token'
    )(bert.model.output)  # shape=[batch_size,maxlen-2,768]

    cnn_features = textcnn(
        all_token_embedding, bert.initializer)  # shape=[batch_size,cnn_output_dim]
    concat_features = keras.layers.concatenate(
        [cls_features, cnn_features],##将两个特征进行拼接
        axis=-1)

    dense = keras.layers.Dense(##全连接层
        units=512,##输出纬度
        activation='relu',##
        kernel_initializer=bert.initializer ##权重初始化
    )(concat_features)

    output = keras.layers.Dense(##输出全连接层
        units=class_nums,##有多少分类类别就有多少神经元
        activation='softmax',#激活函数
        kernel_initializer=bert.initializer
    )(dense)

    model = keras.models.Model(bert.model.input, output)

    return model


if __name__ == '__main__':
    config_path = 'E:/bert_weight_files/bert_wwm/bert_config.json'
    checkpoint_path = 'E:/bert_weight_files/bert_wwm/bert_model.ckpt'
    class_nums = 13
    build_bert_model(config_path, checkpoint_path, class_nums)
