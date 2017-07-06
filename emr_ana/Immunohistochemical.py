import re

class Immunohistochemical():
    def __init__(self):
        self.xrange = range
        sub_code = re.compile('[.,]$')
        self.translate_table = {ord(f): ord(t) for f, t in zip(
            u'。：；，－＊*！？（）、',
            u';:;,-**!?(),')}
        self.sub_func = lambda x: re.sub(sub_code, ';', x)

    def getAll(self, text):
        text = self.sub_func(text.translate(self.translate_table))
        result_dict = dict()
        text = text.strip().replace('\r\n', ' ')
        area_list = self.getArea(text)

        if len(area_list) < 1:
            area_list.append(u'补')
        text_parts = text.split(';')
        for i in self.xrange(0, len(text_parts)):
            text_part = text_parts[i].strip()
            if text_part == '':
                continue
            flag = 0
            for j in self.xrange(0, len(area_list)):
                area_string = area_list[j]
                if area_string in text_part:
                    area_indx_end = text_part.find(area_string) + len(area_string)
                    result_dict[area_string] = self.getIterm(text_part, area_indx_end, len(text_part))
                    area_list.remove(area_string)
                    flag = 1
                    break
            if flag == 0:
                if u'未知' in result_dict:
                    result_dict[u'未知'].update(self.getIterm(text_part, 0, len(text_part)))
                else:
                    result_dict[u'未知'] = self.getIterm(text_part, 0, len(text_part))

        full = []
        for result in result_dict:
            if result.strip() == '':
                continue
            tmp = {'样本号': result}
            for (key, value) in result_dict[result].items():
                tmp.update({key: value})
            full.append(tmp)
        return {'免疫组化': full}

    def getArea(self, text):
        sample_No = []
        pattern1 = re.compile('M[0-9]{4}[－|-|～|-][0-9]{4}|^[^(]+:{1}')
        results = pattern1.findall(text)
        if len(results) < 1:
            pass
        else:
            sample_No.append(results[0].replace(':', ''))

        pattern2 = re.compile(u';([^(][\u4e00-\u9fa5]+?)[:+|[A-Za-z]+')
        results = pattern2.findall(text)
        if len(results) < 1:
            pass
        else:
            for result in results:
                sample_No.append(result.replace(';', '').replace(':', ''))
        return sample_No

    def getIterm(self, text, indx_start, index_end):
        final_res = dict()
        pattern = re.compile('[^;]{1,}?\\(.{1,}?\\)')
        results = pattern.findall(text, indx_start, index_end)
        for result in results:
            result = result.replace(',', '', 1).replace(':', '')
            fields = result.split('(')
            if len(fields) < 2:
                continue
            final_res[fields[0].strip().replace('-', '')] = fields[1].split(')')[0].strip()
        return final_res
