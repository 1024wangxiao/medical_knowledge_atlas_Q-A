# coding=utf-8
import keras
from modules.blistm_crf.crf_layer import CRF

class BiLstmCrfModel(object):
    def __init__(
            self, 
            max_len, 
            vocab_size, 
            embedding_dim, 
            lstm_units, 
            class_nums,
            embedding_matrix=None
        ):
        super(BiLstmCrfModel, self).__init__()
        self.max_len = max_len
        self.vocab_size = vocab_size
        self.embedding_dim = embedding_dim
        self.lstm_units = lstm_units
        self.class_nums = class_nums
        self.embedding_matrix = embedding_matrix
        if self.embedding_matrix is not None:
            self.vocab_size,self.embedding_dim = self.embedding_matrix.shape

    def build(self):
        inputs = keras.layers.Input(
                shape=(self.max_len,), 
                dtype='int32'
            )
        x = keras.layers.Masking(
                mask_value=0#尽最大可能减少padding最模型训练的影响
            )(inputs)
        x = keras.layers.Embedding(
                input_dim=self.vocab_size,
                output_dim=self.embedding_dim,
                trainable=False,
                weights=self.embedding_matrix,
                mask_zero=True
            )(x)
        x = keras.layers.Bidirectional(#双向lstm层
                keras.layers.LSTM(
                    self.lstm_units,
                    return_sequences=True#需要把每个字的表达作为输出
                )
            )(x)
        x = keras.layers.TimeDistributed(
                keras.layers.Dropout(#对lstm的每一个token做dropout，防止过拟合
                    0.2
                )
            )(x)
        crf = CRF(self.class_nums)
        outputs = crf(x)
        model = keras.Model(inputs=inputs, outputs=outputs)
        model.compile(
            optimizer='adam', #优化器
            loss=crf.loss_function, #损失函数
            metrics=[crf.accuracy]#指标，不是完整实体的卷起率，而是每个token的
            )
        print(model.summary())

        return model
        