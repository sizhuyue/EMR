import re


class Microscope:
    def __init__(self):
        self.translate_table = {ord(f): ord(t) for f, t in zip(
            u'：；。，－＊*！？（）、',
            u':, ,-**!?(),')}
        self.CE_table = {ord(f): ord(t) for f, t in zip(
            u'：；。，－＊*！？（）、',
            u':   -**  (),')}
        self.Ss_table = {ord(f): ord(t) for f, t in zip(
            u'。；;！？（）',
            u'     ()')}
        self.Ss_table1 = {ord(f): ord(t) for f, t in zip(
            u',:：；。，－＊*！？（）、',
            u'      -**  () ')}
        self.filter_table = {ord(f): ord(t) for f, t in zip(
            u';、,:：；。，－＊*！？（）',
            u' ,,    ,-**  () ')}
        self.r_table = {ord(f): ord(t) for f, t in zip(
            u',',
            u' ')}

        self.mvi_code = re.compile('癌栓|瘤栓|卫星灶|多灶性')
        self.T = ['少量', '有', '见', '主要呈', '少量', '可见', '主要呈', '呈']
        self.F = ['未见', '未见']
        self.T_code = re.compile("并见|可见|偶见|同主瘤")
        self.mvi = 'MVI'
        self.ddt = re.compile('有|见|少量|可见|未见|无|主要呈|呈')

        self.p1 = re.compile('组织|排列|病灶|肿块')
        self.p2 = re.compile('呈|均为|构成|为|内|由')

        a = ['分化成熟', '菊形团样结构', '束', '增生', '腺样', '松散片', '细梁', '条索', '粗梁', '编织', '团片', '梁索', '假腺管', '巢片', '羽毛', '腺管',
             '旋涡',
             '炎性纤维结缔', '筛', '巢', '不规则扩张的毛细血管网', '透明细胞', '鳞状细胞癌', '漩涡', '硬化', '凝固性坏死', '无一定形结构的坏死', '巢团', '乳头']
        b = '(' + '|'.join(['型', '状', '形', '结构']) + ')?'
        c = [x + b for x in a]
        self.full_pattern = re.compile('|'.join(c))

        ks = ['Masson', 'AB', '网染', 'VG', '铁染色', 'Masson染色', 'AB染色', '网']
        vs = ['\+', '\-']
        self.k_code = re.compile('|'.join(ks))
        self.v_code = re.compile('|'.join(vs))
        self.PLS_code = re.compile('假小叶结构')

    def getAll(self,query):
        res = {"镜下所见":{},"特殊染色":self.get_SStain(query)}
        kv_list = [('组织类型',self.get_orz_shape(query)),
                   ('肉眼类型',self.set_null()),
                   ('血管癌栓',self.parse_MVI(query)),
                   ('假小叶结构',self.DDPLS(query))]
        [res['镜下所见'].update({k:v}) for k,v in kv_list]
        return res

    def set_null(self):
        return 'null'

    def DDPLS(self, query):
        re_query = query.translate(self.translate_table)
        re_seq = re_query.split(',')
        for seq in re_seq:
            a = re.search(self.PLS_code, seq)
            if a:
                s = re.search(self.ddt, seq)
                if s:
                    if s.group() in self.T:
                        return '有'
                    else:
                        return '无'
        return 'null'

    def parse_MVI(self, query):
        mvi_value = 0
        re_query = query.translate(self.CE_table)
        for i in re_query.split():
            if re.search(self.mvi_code, i):
                tmp_i = re.sub(self.T_code, '有', i)
                s_code = re.search(self.ddt, tmp_i)
                if s_code:
                    status = s_code.group()
                    if status in self.T:
                        mvi_value += 1
        if mvi_value != 0:
            return '有'
        else:
            return '无'

    def get_SStain(self, query):
        res = []
        tmp_res = {'样本号':'未知'}
        re_query = query.translate(self.Ss_table)
        for text in re_query.split():
            if re.search(self.k_code, text):
                re_text = text.translate(self.Ss_table1)
                for item in re_text.split():
                    k_s = re.search(self.k_code, item)
                    v_s = re.search(self.v_code, item)
                    if k_s and v_s:
                        k = k_s.group()
                        v = v_s.group()
                        tmp_res.update({k:v})
        res.append(tmp_res)
        if not res:
            res = 'null'
        return res

    def get_SStain_full(self, query):
        res = {'特殊染色':[]}
        tmp_res = {}
        re_query = query.translate(self.Ss_table)
        for text in re_query.split():
            if re.search(self.k_code, text):
                re_text = text.translate(self.Ss_table1)
                for item in re_text.split():
                    k_s = re.search(self.k_code, item)
                    v_s = re.search(self.v_code, item)
                    if k_s and v_s:
                        k = k_s.group()
                        v = v_s.group()
                        tmp_res.update({k:v})
        if not tmp_res:
            tmp_res = {'null':'null'}
        else:
            tmp_res.update({'样本号':'未知'})
        res['特殊染色'].append(tmp_res)
        return res

    def get_orz_shape(self, query):
        re_query = query.translate(self.filter_table)
        for chunk in re_query.split():
            if re.search(self.p1, chunk) and re.search(self.p2, chunk):
                s = re.search(self.full_pattern, chunk)
                if s:
                    return s.group()
        return 'null'
