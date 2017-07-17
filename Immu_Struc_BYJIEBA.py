import codecs
import jieba
import jieba.posseg as pseg
import pandas
import re


class ImmuStructure():
    def __init__(self):
        jieba.initialize()
        pseg.re_han_internal = re.compile("([ βα\u4E00-\u9FD5a-zA-Z0-9+#&／<.\[_\]\-%~//]+)", re.U)
        pseg.re_han_detail = re.compile("([\u4E00-\u9FD5]+)", re.U)
        self.translate_table = {ord(f): ord(t) for f, t in zip(
            '；：（），／＊、。—{}＞％～－',
            ';:(),/*和;-[]>%~-')}
        self.addition_word = ['膜+', '灶+']  # 存储一些切词结果tag错误的词
        self.regex_sampleNo = '[0-9]{2}S[0-9]{5}[-][0-9]{3}|M[0-9]{4}[-~][0-9]{4}|^[^(]+:{1}'
        self.Meaningless = []
        self.synonym_dict = dict()
        self.standard_dict = dict()
        self.addWord2jieba('emr_ana/emr_ana_data/synonym_IHC.txt', 'emr_ana/emr_ana_data/Dictionary_IHC.txt')
        self.Loadmeaningless('emr_ana/emr_ana_data/meanLess.txt')
        # self.addWord2jieba('D:/data/dict/synonym_IHC.txt', 'D:/data/dict/Dictionary_IHC.txt')
        # self.Loadmeaningless('D:/data/dict/meanLess.txt')

    ################加载同义词的词典，并保存###############
    def loadSyno(self, filePath):
        synoFile = codecs.open(filePath, mode='r', encoding='utf8')
        for line in synoFile:
            line = line.strip('\r\n')
            fields = line.split('\t')
            various_writing = fields[0]
            standard_writing = fields[1]
            self.synonym_dict[various_writing.upper()] = standard_writing.upper()
        synoFile.close()

    ###########加载标准词典，并保存###################
    def loadStanddict(self, filePath):
        dict_file = codecs.open(filePath, mode='r', encoding='utf8')
        for line in dict_file:
            line = line.strip('\r\n')
            fields = line.split('\t')
            standard_writing = fields[0]
            tag = fields[1]
            self.standard_dict[standard_writing.upper()] = tag
        dict_file.close()

    ###############向jieba中添加词典#################
    def addWord2jieba(self, syn_file, stand_file):
        self.loadSyno(syn_file)
        self.loadStanddict(stand_file)
        for word in self.synonym_dict:  # 为各种写法加上tag
            standard_writing = self.synonym_dict[word]
            if standard_writing in self.standard_dict:
                tag = self.standard_dict[standard_writing]
                jieba.add_word(word, 1000, tag)
            else:
                print(word + ' not in standard_dict! please check!')

    def Loadmeaningless(self, filePath):
        inputfile = codecs.open(filePath, mode='r', encoding='utf8')
        for line in inputfile:
            line = line.strip('\r\n')
            line = self.normalize(line)
            self.Meaningless.append(line)
        inputfile.close()

    ###########归一化（特殊符号处理）###########
    def normalize(self, text):
        text = text.translate(self.translate_table)
        text =re.sub('例如:','',text).upper()
        text = text.replace('<', '小于').replace('>', '大于')
        text = text.replace(' ', '')
        return text

    ##################获取切词结果#############
    def getCutRes(self, text):
        return pseg.lcut(text)

    ################读文件####################
    def readFromCSV(self, filepath):
        dataFrame = pandas.read_csv(filepath, low_memory=False)
        inspect_conclu = dataFrame['检查结论'].dropna()
        return inspect_conclu

    #################获取切词结果中标志物跟着的词################
    def getValueStru(self, cut_res, indx):
        win = 10
        i = 1
        prob_array = []  # 存储标志物后面接着的词
        extract_res = dict()
        res = dict()
        res_list = []
        marker = cut_res[indx].word
        if marker in self.synonym_dict:  # 将标志物转为标准写法
            marker = self.synonym_dict[marker]
        hasYinYang = False
        pn_count = 0
        while (i < win and (indx + i) < len(cut_res) and cut_res[
                indx + i].flag != 'ihc-mark'):  # 从index开始找标志物，直到找到下一个标志物为止
            w = cut_res[indx + i]
            if w.word == '基因':
                return
            if w.flag == 'ihc-pn':
                hasYinYang = True
                pn_count += 1
            if w.flag in ['ihc-mark', 'ihc-sec', 'ihc-pn', 'ihc-desc', 'ihc-num']:
                prob_array.append(w)
            i += 1
        if not hasYinYang:  # 如果根本找不到描述阴阳性的词，则直接返回
            return
        if pn_count == len(prob_array):  # 如果整个prob_array里面只有描述阴阳性的词，则只要第一个阴阳性
            prob_array = [prob_array[0]]
        last_region = 'null'
        for i in range(len(prob_array)):
            w = prob_array[i]
            if w.flag in ['ihc-mark', 'ihc-sec', 'ihc-pn', 'ihc-desc', 'ihc-num']:
                if w.flag != 'ihc-sec':  # 在没找到切片区域之前，一直追加标准写法
                    if w.word in self.synonym_dict:
                        res_list.append(self.synonym_dict[w.word])
                    else:
                        res_list.append(w.word)
                else:  # 找到切片区域了，判断一下res_list是否为空，不为空的话，将切片区域设置为key，res_list转为string设置为value，并将res_list清空，为下一个切片区域做准备
                    if len(res_list) > 0:
                        res[last_region] = ''.join(res_list)
                    res_list.clear()
                    last_region = w.word
        res[last_region] = ''.join(res_list)
        if 'null' in res:  # 如果无切片区域，直接将“null”的值赋给切片区域
            add_word = res['null']
            if add_word in self.addition_word:
                res.pop('null')
                res[add_word[0]] = add_word[1]
                extract_res[marker] = res
            else:
                extract_res[marker] = res['null']
        else:
            extract_res[marker] = res
        return extract_res

    ######################对文本按照样本号进行切割#################
    def SegText(self, text):
        seg_text = []
        fields = re.split(self.regex_sampleNo, text)
        results = re.compile(self.regex_sampleNo).findall(text)
        seg_text.append(fields[0])
        for i in range(len(results)):
            union_string = results[i] + fields[i + 1]
            seg_text.append(union_string)
        return seg_text

    def getAll(self, seg_text):
        res = dict()
        area = '未知'
        for text in seg_text:
            tmp = re.compile(self.regex_sampleNo).search(text)
            if tmp:  # 如果用正则能得到样本号（area表示样本号）
                area = tmp.group()
            cut_res = self.getCutRes(text)
            for indx, w in enumerate(cut_res):
                if w.flag == 'ihc-mark':
                    value_dict = self.getValueStru(cut_res, indx)
                    if not value_dict:
                        continue
                    if area in res:  # 如果样本号已经存过，则更新其结构
                        res[area].update(value_dict)
                    else:  # 否则，直接给值
                        res[area] = value_dict
        new_res = []
        for k, v in res.items():
            v.update({'样本号': k})
            new_res.append(v)
        return new_res

    def main_func(self, text):
        text = self.normalize(text)
        for sentence in self.Meaningless:
            text = text.replace(sentence, '')
        seg_text = self.SegText(text)
        final_res = self.getAll(seg_text)
        return final_res


# if __name__ == '__main__':
#     immu=ImmuStructure()
#     # texts=immu.readFromCSV('D:/data/2016-PD-L1-1129.csv')
#     # outputFile=codecs.open('immu_res.txt',mode='w',encoding='utf8')
#     # for text in texts:
#     #     #print(text)
#     #     res=immu.main_func(text)
#     #     jsObj = json.dumps(res,ensure_ascii=False)
#     #     outputFile.write(text+'\t'+jsObj+'\n')
#     # outputFile.close()
#     text="""(肝右叶) 肝细胞肝癌(2灶)，III级，伴子灶形成，肝切缘未见癌累及。周围肝组织结节性肝硬化（G2S4），伴肝细胞脂肪变性约10%。（胆囊）慢性炎伴罗阿氏窦形成。预后 指标术式:部分肝 多发肿瘤：数目(N=2
#     ),大小(最大者直径2 cm，最小者直径 1.5cm)肉眼类型:多结节型 组织类型:肝细胞癌(粗梁型,团片型)分级:肝细胞癌(III) 卫星灶:无脉管侵犯: （巨检／手术所见）：无 微脉管侵犯（显微镜下所见）：有　＊
#     累及脉管数量累犯脉管最远距离(mm)悬浮癌细胞≤50个/＞50个门脉分支(包括肿瘤包膜)  >50肝静脉分支   肝动脉分支   淋　巴　管  MVI提示风险分级：●M1（低危组）,
#     ≤5个MVI，且发生于近癌旁肝组织（≤1cm）切除面:未有癌,距肿瘤最近距离0.5cm 小胆管癌栓:无肝被膜:未侵犯 胆管侵犯:无癌周围肝组织:无肝细胞大、小细胞变 周围神经侵犯:无肝硬化:有 远处转移:未知肝炎:有,
#     肝炎程度G2 纤维化分期S4 淋巴结:无淋巴结胆囊侵犯:无 另送膈肌:无邻近组织侵犯:未知 免疫组化（2016-N04358)： 16S09193-001：ALK[克隆号D5F3,Ventana](-),ARID1a(+),
#     CD34(血窦丰富),CK19(部分+),CK7(少量+),C-MET(-),Hepa(+),Ki-67(10%+),PD-1(-),PD-L1(-),TSC2(部分+)  16S09193-006：ALK[克隆号D5F3,
#     Ventana](-),ARID1a(+),CD34(血窦丰富),CK19(-),CK7(部分+),C-MET(-),Hepa(+),Ki-67(25%+),PD-1(-),PD-L1(肿瘤20%+,间质20%+),
#     TSC2(部分+) """
#     res=immu.main_func(text)
#     print(res,len(res[0].keys()))