#coding:utf8
import pandas
import jieba
import jieba.posseg as pseg
import json
import re
import codecs
import random


jieba.initialize()
jieba.load_userdict('all_dict.dict')
outputFile=codecs.open('res_test',mode='w',encoding='utf8')

class EMRStructure():
    def main_func(self,filePath):
        [pathologic_diagnosis, immunohistochemistry,grossApperance]=self.readFromCSV(filePath)
        ##########################病理诊断########################
        # for sentence_str in pathologic_diagnosis:
        #     sentence_str=str(sentence_str).upper().replace('、','').replace('（','(').replace('）',')')
        #     if sentence_str!='NAN':
        #         print sentence_str
        #         self.path_diag = PathologyDiag(sentence_str)
        #         self.path_diag.getAll(sentence_str)

        ###########################免疫组化#######################

        for sentence_str in immunohistochemistry:
            sentence_str = str(sentence_str).upper().replace('；', ';').replace('（', '(').replace('）', ')').replace('。',';').replace('，',',').replace('：',':')
            if sentence_str[-1]==',' or sentence_str[-1]=='.':
                sentence_str=sentence_str[0:len(sentence_str)-1]+';'
            if sentence_str!='NAN':
                #print sentence_str
                self.immu=Immunohistochemical(sentence_str)
                self.immu.getAll(sentence_str)


        #########################肉眼所见########################
        # for sentence_str in grossApperance:
        #     sentence_str=str(sentence_str).upper().replace('，',',').replace('；',';')
        #     if sentence_str!='NAN':
        #         ga=GrossApperance()
        #         ga.getAll(sentence_str)


        outputFile.close()

    def readFromCSV(self,filepath):
        dataFrame=pandas.read_csv(filepath, low_memory=False)
        #pathologic_diagnosis=dataFrame.get('病理诊断')
        pathologic_diagnosis=dataFrame.get('检查结论')
        immunohistochemistry=dataFrame.get('特殊检查')
        grossApperance=dataFrame.get('肉眼所见')
        return pathologic_diagnosis,immunohistochemistry,grossApperance



#############################################病理诊断#################################################
class PathologyDiag():
    def __init__(self,text):
        self.cut_res=pseg.cut(text)#获取切词结果
        self.ptype=[]
        self.pos=[]
    def getAll(self,text):
        for w in self.cut_res:
            if w.flag=='ptype':
                self.ptype.append(w.word)
                #print 'first----' + w.word + '/' + w.flag
            if w.flag=='pos':
                self.pos.append(w.word)
                #print 'first----'+w.word+'/'+w.flag
        text=text.strip().replace('\r\n',' ')
        text = text.decode('utf8')
        position=self.getPos(text)   # 部位
        mvi=self.getMVI(text)        # MVI分级
        ptype=self.getPType()    # 患病类型
        dif=self.getDif(text)        # 分化程度
        hepatitis=self.getHepatitis(text)  #肝炎分期

        path_dict=dict()
        path_dict['患病部位']=position
        path_dict['患病类型']=ptype
        path_dict['分化程度']=dif
        path_dict['MVI分级']=mvi
        path_dict['肝炎分期']=hepatitis

        #jsObj = json.dumps(path_dict)
        # outputFile.write(jsObj)
        # outputFile.write(text+'\n')
        # outputFile.write(u'患病部位：%s;患病类型:%s;分化程度:%s;MVI分级:%s;肝炎分期:%s\n\n'%(position,ptype,dif,mvi,hepatitis))
        #outputFile.write('%s\t%s\t%s\t%s\t%s\n'%(text,position,ptype,dif,mvi))
        print '患病部位：'+position.encode('utf8')
        print '患病类型：'+ptype.encode('utf8')
        print '分化程度：'+dif.encode('utf8')
        print 'MVI分级：'+mvi.encode('utf8')



#############分化程度##################
    def getDif(self,text):
        result=u'无'
        pattern1 = re.compile(u'[\u2160-\u2163|[I|II|III|IV]+[ |－|-|～|-]*[\u2160-\u2163|[I|II|III|IV]*级')
        results1=pattern1.search(text)
        if results1:
            result= results1.group()
            #print result
        pattern2 = re.compile(u'[中|高|低]+.{0,3}分化|分化[较]*差')
        results2=pattern2.search(text)
        if results2:
            result=results2.group()
            #print result
        return result

############MVI分级###################
    def getMVI(self,text):
        result=u'无'
        pattern = re.compile(r'MVI{1}.{0,10}M\d{1}')
        results=pattern.search(text)
        if results:
            pattern=re.compile(r'M\d{1}')
            result=pattern.search(results.group())
            return result.group()
        else:
            return result

################患病部位###################
    def getPos(self,text):
        result=u'无'
        pattern = re.compile(u'[\(|（][\u4e00-\u9fa5]*[\)|）]')
        results = pattern.search(text)
        if results:
            result=results.group()
            result=result.replace('(','').replace(')','')
            joint_res=[]
            for w in self.pos:
                if w in result:
                    joint_res.append(w)
            if len(joint_res)>1:
                result=u'及'.join(joint_res)
        return result


####################患病类型##############
    def getPType(self):
        if len(self.ptype)>0:
            return self.ptype[0]
        else:
            return u'无'

###############肝炎情况###################
    def getHepatitis(self,text):
        result=u'无'
        pattern = re.compile(r'G[0-9]S[0-9]')
        results=pattern.search(text)
        if results:
            result=results.group()
        return result


######################切词(带tag的)################
    def get_cutRes(self,sentence_str):
        cut_res = pseg.cut(sentence_str)
        return cut_res

#####################################################################免疫组化##################################################################
class Immunohistochemical():
    def __init__(self,text):
        pass

    def getAll(self,text):
        result_dict=dict()
        text = text.strip().replace('\r\n', ' ')
        text = text.decode('utf8')
        area_list=self.getArea(text)
        # for area_string in area_list:
        #     print u'找到部位：' + area_string

        if len(area_list)<1:
            area_list.append(u'补')
        text_parts=text.split(';')
        for i in xrange(0,len(text_parts)):
            text_part=text_parts[i].strip()
            if text_part=='':
                continue
            #print text_part
            flag = 0
            area_indx_end=0
            for j in xrange(0,len(area_list)):
                area_string=area_list[j]
                if area_string in text_part:
                    area_indx_end=text_part.find(area_string)+len(area_string)
                    #print 'start to extract %s from %s at %d:'%(area_string,text_part,area_indx_end)
                    result_dict[area_string]=self.getIterm(text_part,area_indx_end,len(text_part))
                    area_list.remove(area_string)
                    flag=1
                    break
            if flag==0:
                if u'未知' in result_dict:
                    result_dict[u'未知'].update(self.getIterm(text_part,0,len(text_part)))
                else:
                    result_dict[u'未知']=self.getIterm(text_part,0,len(text_part))
                #print result_dict[u'未知']

        print text
        result_string=text
        full = []
        for result in result_dict:
            if result.strip()=='':
                 continue
            #result_string='样本号：%s,各指标：\n'%result.encode('utf8')
            #result_string='%s\t%s---'%(result_string,result)
            print result
            tmp = {'id':result}
            for (key,value) in result_dict[result].iteritems():
                tmp.update({key:value})
            full.append(tmp)
                #print key+':'+value
                #result_string='%s%s:%s;'%(result_string,key.encode('utf8'),value.encode('utf8'))
                # print key+':'+value
                #result_string = '%s%s:%s;' % (result_string, key, value)
        #print result_string
        #outputFile.write(result_string+'\n')
        print full
        print '\n'




    def getArea(self,text):
        sample_No=[]
        ########获取类似M2006-1839这类的样本号###########
        pattern1=re.compile('M[0-9]{4}[－|-|～|-][0-9]{4}|^[^(]+:{1}')
        results=pattern1.findall(text)
        if len(results)<1:
            pass
        else:
            sample_No.append(results[0].replace(':',''))

        ########获取另一区域###############
        pattern2 = re.compile(u';([^(][\u4e00-\u9fa5]+?)[:+|[A-Za-z]+')
        results = pattern2.findall(text)
        if len(results)<1:
            pass
        else:
            for result in results:
                print result
                sample_No.append(result.replace(';','').replace(':',''))

        #########处理",汉字:"这种类型#########
        # pattern3=re.compile(u',([\u4e00-\u9fa5]*?):')
        # results = pattern3.findall(text)
        # if len(results)<1:
        #     pass
        # else:
        #     for result in results:
        #         print result
        #         sample_No.append(result.replace(';', '').replace(':', ''))

        return sample_No

    def getIterm(self,text,indx_start,index_end):
        final_res=dict()
        pattern =re.compile('[^;]{1,}?\\(.{1,}?\\)')
        results=pattern.findall(text,indx_start,index_end)
        for result in results:
            result=result.replace(',','',1).replace(':','')
            #result = result.replace(':', '')
            fields=result.split('(')
            if len(fields)<2:
                continue
            final_res[fields[0].strip().replace('-','').replace(',','')]=fields[1].split(')')[0].strip()
        return final_res




class GrossApperance():
    def __init__(self):
        self.translate_table = {ord(f): ord(t) for f, t in zip(
            u'一二两三四五六七八九',
            u'1223456789')}
    def getAll(self,text):
        text = text.strip().replace('\r\n', ' ')
        text=text.decode('utf8')
        print text
        apperance=dict()
        #self.getCutRes(text)
        [diameter,tumorNum]=self.getDiameter(text) #tumorNum是累加出来的
        cirrhosis=self.getCirrhosis(text)
        tumor_num=self.getTumorNum(text) #tumor_num真正抽取出来的
        apperance['最大直径']=str(diameter)
        apperance['肝炎类型']=cirrhosis

        if tumor_num>99:
            apperance['肿块数量']=u'多个'
            return apperance
        if tumor_num<tumorNum:
            apperance['肿块数量']=str(tumorNum)
        else:
            apperance['肿块数量']=str(tumor_num)
        print apperance
        return apperance


        # if tumor_num<tumorNum and tumorNum!=100:
        #     outputFile.write('%s\t%d\t%f\t%s\n'%(text,tumorNum,diameter,cirrhosis))
        # elif tumorNum==100:
        #     outputFile.write('%s\t多个\t%f\t%s\n'%(text,diameter,cirrhosis))
        # else:
        #     outputFile.write('%s\t%d\t%f\t%s\n' % (text,tumor_num,diameter, cirrhosis))
        # # outputFile.write('%s\t%d\t%f\t%s\n'%(text,tumorNum,diameter,cirrhosis))

    def getDiameter(self,text):
        text=re.sub(ur'(肿块|结节|肿瘤).{0,8}?(大小|最大)',u'肿块',text)
        #print text
        final_result=[]
        max_diameter=0.0
        pattern1 = re.compile(ur'(肿块|结节|肿瘤)[^×]{0,5}?([0-9]+\.{0,1}[0-9]{0,1}[CM]*?×[0-9]+\.{0,1}[0-9]{0,1}CM)')
        results = pattern1.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                final_result.append(res_string)
                print u'直径 from pattern1：' + res_string
                res_string=res_string.replace('CM','')
                fields=res_string.split(u'×')
                if len(fields)<2:
                    continue
                first_num=float(fields[0])
                second_num=float(fields[1])
                # print first_num
                # print second_num
                if max_diameter< first_num:
                    max_diameter=first_num
                if max_diameter< second_num:
                    max_diameter=second_num


        pattern2=re.compile(ur'(肿块|结节|肿瘤).{0,5}?直径.*?([0-9]+\.{0,1}[0-9]{0,1}CM)')
        results = pattern2.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                print u'直径 from pattern2：' + res_string
                res_string=float(res_string.replace('CM',''))
                if max_diameter< res_string:
                    max_diameter=res_string
                final_result.append(res_string)


        pattern3 = re.compile(ur'(肿块|结节|肿瘤).{0,5}直径.*?[和|、]([0-9]+\.{0,1}[0-9]{0,1}CM)')
        results = pattern3.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                print u'直径 from pattern3：' + res_string
                res_string = float(res_string.replace('CM', ''))
                if max_diameter< res_string:
                    max_diameter=res_string
                final_result.append(res_string)


        pattern4 = re.compile(ur'(肿块|结节|肿瘤).*?[和|、]([0-9]+\.{0,1}[0-9]{0,1}[CM]*?×[0-9]+\.{0,1}[0-9]{0,1}[CM]*?)')
        results = pattern4.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                final_result.append(res_string)
                print u'直径 from pattern4：' + res_string
                res_string=res_string.replace('CM','')
                fields=res_string.split(u'×')
                if len(fields)<2:
                    continue
                first_num=float(fields[0])
                second_num=float(fields[1])
                # print first_num
                # print second_num
                if max_diameter< first_num:
                    max_diameter=first_num
                if max_diameter< second_num:
                    max_diameter=second_num


        print u'最大直径：%.2f'%max_diameter
        print u'肿瘤个数：%d'%len(final_result)
        return max_diameter,len(final_result)


    def getCirrhosis(self,text):
        final_result='null'
        if u'肝硬化不明显' in text or u'无肝硬化' in text:
            return u'无'
        pattern=re.compile(ur'(?:余肝|呈)([\u4e00-\u9fa5]*)肝硬[化变]')
        results=pattern.findall(text)
        for result in results:
            if u'无' in result or u'未见' in result:
                print u'肝硬化类型：无'
                final_result=u'无'
            else:
                print u'肝硬化类型：'+result.replace(u'呈','')
                final_result=result.replace(u'呈','')
        return final_result

    def getTumorNum(self,text):
        tumor_num=0
        pattern1=re.compile(ur'(?:结节|肿块|肿瘤)[^;型]{0,10}([一二三四五六七八九多\d]+[个枚])')
        results=pattern1.findall(text)
        for result in results:
            print u'肿瘤个数 in pattern1:'+result
            tmp_v = self.string2int(result)
            if tmp_v:
                if tmp_v > tumor_num:
                    tumor_num = tmp_v

        pattern3=re.compile(ur'.*(.+?个).{0,5}?(?:结节|肿块|肿瘤)[^型标本]')
        results=pattern3.findall(text)
        for result in results:
            print u'肿瘤个数 in pattern3:'+result
            tmp_v = self.string2int(result)
            if tmp_v:
                if tmp_v > tumor_num:
                    tumor_num = tmp_v

        pattern2 = re.compile(ur'均为.*?色{0,1}(?:肿块|结节|肿瘤)')
        results = pattern2.findall(text)
        if len(results)>= 1:
            print u'肿瘤个数 in pattern2:均为'
            tmp_v = self.string2int(u'多')
            if tmp_v:
                if tmp_v > tumor_num:
                    tumor_num = tmp_v

        return float(tumor_num)

    def string2int(self,tumor_num):
        tumor_num = tumor_num.replace(u'枚', '').replace(u'个', '')
        tumor_num = tumor_num.translate(self.translate_table)
        if tumor_num == u'多' or tumor_num == u'数':
            tumor_num = 100
        if str(tumor_num).isdigit():
            return int(tumor_num)
        else:
            return False

    def getCutRes(self,text):
        cut_res=list(pseg.cut(text))
        for i in xrange(0,len(cut_res)):
            w=cut_res[i]
            if w.word==u'个':
                res=cut_res[i-1].word
                print text
                print '%d:%s%s/%s'%(i,res,w.word,w.flag)










if __name__ == '__main__':
    emr=EMRStructure()
    emr.main_func('D:/data/DFGDRaw.csv')
    #emr.main_func('D:/data/2016-PD-L1-1129.csv')
    ######免疫组化测试#####
    # mianyi=Immunohistochemical('null')
    # str='HEP-1(+),HBSAG(+),CK18(+),CK19(-),CD34(+),GLY-3(+),CD10(+);游离组织灰白色结节HEP-1(-),CK19(+);'
    # str=str.upper().replace('；', ';').replace('（', '(').replace('）', ')').replace('。',';').replace('，',',').replace('：',':')
    # if str[-1]==',':
    #     str=str[0:len(str)-1]+';'
    # mianyi.getAll(str)

    ######肉眼所见测试######
    # rouyansuojian=GrossApperance()
    # string='肝脏标本19.2×12.4×6.1CM,切面可见灰白色肿块5个,大小分别为4×3CM、3.6×3.2CM、2.5×2.1CM、2.4×2.2CM、2.4×1.9CM,周边有部分包膜,第二个严重坏死,肿瘤紧贴肝切缘,余肝呈混合结节型肝硬化;胆囊10.2×3.1CM,壁厚0.2-0.3CM,黏膜粗糙'
    # string=string.upper().replace('，',',').replace('；',';')
    # rouyansuojian.getAll(string)