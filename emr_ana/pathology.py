import jieba
import jieba.posseg as pseg
import re
#from server_info import base_path

#############################################病理诊断#################################################
class PathologyDiag():
    def __init__(self):
        jieba.initialize()
        jieba.load_userdict('emr_ana/emr_ana_data/all_dict.dict')

    def getAll(self, text):
        self.ptype = []
        self.pos = []
        self.cut_res = pseg.cut(text)  # 获取切词结果
        for w in self.cut_res:
            if w.flag == 'ptype':
                self.ptype.append(w.word)
                # print 'first----' + w.word + '/' + w.flag
            if w.flag == 'pos':
                self.pos.append(w.word)
                # print 'first----'+w.word+'/'+w.flag
        text = text.strip().replace('\r\n', ' ')
        #         text = text.decode('utf8')
        position = self.getPos(text)  # 部位
        mvi = self.getMVI(text)  # MVI分级
        ptype = self.getPType()  # 患病类型
        dif = self.getDif(text)  # 分化程度
        hepatitis = self.getHepatitis(text)  # 肝炎分期

        path_dict = dict()
        [path_dict.update({key: value}) if value else path_dict.update({key: 'null'}) for key, value in
         [('患病部位', position),
          ('患病类型', ptype),
          ('分化程度', dif),
          ('MVI分级', mvi),
          ('肝炎分期', hepatitis)]]

        return {'诊断结论': path_dict}

    #############分化程度##################
    def getDif(self, text):
        result = 'null'
        pattern1 = re.compile(u'[\u2160-\u2163|[I|II|III|IV]+[ |－|-|～|-]*[\u2160-\u2163|[I|II|III|IV]*级')
        results1 = pattern1.search(text)
        if results1:
            result = results1.group()
            # print result
        pattern2 = re.compile(u'[中|高|低]+.{0,3}分化|分化[较]*差')
        results2 = pattern2.search(text)
        if results2:
            result = results2.group()
            # print result
        return result

    ############MVI分级###################
    def getMVI(self, text):
        result = 'null'
        pattern = re.compile(r'(MVI|MVⅠ){1}.{0,10}M\d{1}')
        results = pattern.search(text)
        # print('123123')
        if results:
            # print('results: ', results.group())
            pattern = re.compile(r'M\d{1}')
            result = pattern.search(results.group())
            return result.group()
        else:
            return result

            ################患病部位###################

    def getPos(self, text):
        result = 'null'
        pattern = re.compile(u'[\(|（][\u4e00-\u9fa5]*[\)|）]')
        results = pattern.search(text)
        if results:
            result = results.group()
            result = result.replace('(', '').replace(')', '')
            joint_res = []
            for w in self.pos:
                if w in result:
                    joint_res.append(w)
            if len(joint_res) > 1:
                result = u'及'.join(joint_res)
        return result

    ####################患病类型##############
    def getPType(self):
        if len(self.ptype) > 0:
            return self.ptype[0]
        else:
            return 'null'

            ###############肝炎情况###################

    def getHepatitis(self, text):
        result = 'null'
        pattern = re.compile(r'G[0-9]S[0-9]')
        results = pattern.search(text)
        if results:
            result = results.group()
        return result

    ######################切词(带tag的)################
    def get_cutRes(self, sentence_str):
        cut_res = pseg.cut(sentence_str)
        return cut_res
