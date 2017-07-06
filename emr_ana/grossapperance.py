import re


class GrossApperance():
    def __init__(self):
        self.translate_table = {ord(f): ord(t) for f, t in zip(
            u'一二两三四五六七八九',
            u'1223456789')}

    def getAll(self, text):
        text = text.upper().replace('，', ',').replace('；', ';')
        text = text.strip().replace('\r\n', ' ')
        apperance = dict()
        [diameter, tumorNum] = self.getDiameter(text)  # tumorNum是累加出来的
        cirrhosis = self.getCirrhosis(text)
        tumor_num = self.getTumorNum(text)  # tumor_num真正抽取出来的
        apperance['最大直径'] = str(diameter)
        apperance['肝硬化'] = cirrhosis

        if tumor_num > 99:
            apperance['肿块数量'] = u'多个'
        elif tumor_num < tumorNum:
            apperance['肿块数量'] = str(tumorNum)
        else:
            apperance['肿块数量'] = str(tumor_num)
        return {'肉眼所见':apperance}


    def getDiameter(self, text):
        text = re.sub(u'(肿块|结节|肿瘤).{0,8}?(大小|最大)', u'肿块', text)
        final_result = []
        max_diameter = 0.0
        pattern1 = re.compile(u'(肿块|结节|肿瘤)[^×]{0,5}?([0-9]+\.{0,1}[0-9]{0,1}[CM]*?×[0-9]+\.{0,1}[0-9]{0,1}CM)')
        results = pattern1.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                final_result.append(res_string)
                res_string = res_string.replace('CM', '')
                fields = res_string.split(u'×')
                if len(fields) < 2:
                    continue
                first_num = float(fields[0])
                second_num = float(fields[1])
                # print first_num
                # print second_num
                if max_diameter < first_num:
                    max_diameter = first_num
                if max_diameter < second_num:
                    max_diameter = second_num

        pattern2 = re.compile(u'(肿块|结节|肿瘤).{0,5}?直径.*?([0-9]+\.{0,1}[0-9]{0,1}CM)')
        results = pattern2.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                res_string = float(res_string.replace('CM', ''))
                if max_diameter < res_string:
                    max_diameter = res_string
                final_result.append(res_string)

        pattern3 = re.compile(u'(肿块|结节|肿瘤).{0,5}直径.*?[和|、]([0-9]+\.{0,1}[0-9]{0,1}CM)')
        results = pattern3.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                res_string = float(res_string.replace('CM', ''))
                if max_diameter < res_string:
                    max_diameter = res_string
                final_result.append(res_string)

        pattern4 = re.compile(u'(肿块|结节|肿瘤).*?[和|、]([0-9]+\.{0,1}[0-9]{0,1}[CM]*?×[0-9]+\.{0,1}[0-9]{0,1}[CM]*?)')
        results = pattern4.findall(text)
        for result in results:
            for res_string in result:
                if res_string in u'肿块结节肿瘤':
                    continue
                final_result.append(res_string)
                res_string = res_string.replace('CM', '')
                fields = res_string.split(u'×')
                if len(fields) < 2:
                    continue
                first_num = float(fields[0])
                second_num = float(fields[1])
                if max_diameter < first_num:
                    max_diameter = first_num
                if max_diameter < second_num:
                    max_diameter = second_num

        return max_diameter, len(final_result)

    def getCirrhosis(self, text):
        final_result = 'null'
        if u'肝硬化不明显' in text or u'无肝硬化' in text:
            return u'无'
        pattern = re.compile(u'(?:余肝|呈)([\u4e00-\u9fa5]*)肝硬[化变]')
        results = pattern.findall(text)
        for result in results:
            if u'无' in result or u'未见' in result:
                final_result = u'无'
            else:
                final_result = result.replace(u'呈', '')
        return final_result

    def getTumorNum(self, text):
        tumor_num = '0'
        pattern1 = re.compile(u'(?:结节|肿块|肿瘤)[^;型]{0,10}([一二三四五六七八九多数\d]+[个枚])')
        results = pattern1.findall(text)
        for result in results:
            tumor_num = result

        pattern3 = re.compile(u'.*(.+?个).{0,5}?(?:结节|肿块|肿瘤)[^型标本]')
        results = pattern3.findall(text)
        for result in results:
            tumor_num = result

        pattern2 = re.compile(u'均为.*?色{0,1}(?:肿块|结节|肿瘤)')
        results = pattern2.findall(text)
        if len(results) >= 1:
            tumor_num = u'多'

        tumor_num = tumor_num.replace(u'枚', '').replace(u'个', '')
        tumor_num = tumor_num.translate(self.translate_table)
        if tumor_num == u'多' or tumor_num == u'数':
            tumor_num = 100
        return float(tumor_num)
