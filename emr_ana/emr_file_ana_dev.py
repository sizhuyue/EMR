import json
import pandas as pd
from emr_ana import Immunohistochemical, pathology, grossapperance
from emr_ana.microscope import Microscope
import codecs

immunohistochemical = Immunohistochemical.Immunohistochemical()
microscope = Microscope()
pathology = pathology.PathologyDiag()
grossapperance = grossapperance.GrossApperance()
feed = lambda x: x


func_map = {'预后指标': '',
            '诊断结论': pathology.getAll,
            '免疫组化': immunohistochemical.getAll,
            '基因检测': '',
            '镜下所见': microscope.getAll,
            '肉眼所见': grossapperance.getAll,
            '特殊染色': microscope.get_SStain_full,
            '血清检查': '',
            '肿瘤直径': feed,
            'Diagnosis	': feed,
            'HBV': feed,
            'HCV': feed,
            'CA19.9': feed,
            'AFP': feed
            }


def emr_ana_dev(query, dt):
    res = {}
    if query:
        if isinstance(dt, list):  # 如果是list类型
            for d in dt:
                func = func_map.get(d)
                if func:
                    try:
                        res.update(func(query))  # 针对每个调用其对应的函数
                    except:
                        res.update({d:func(query)})
        elif isinstance(dt, str):  # 如果只是单个的字符串（表示只需要获取其中一个的格式化)
            func = func_map.get(dt)
            if func:
                tmp_value = func(query)
                if isinstance(tmp_value,dict):
                    res.update(tmp_value)
                else:
                    res.update({dt:tmp_value})
    if res:
        return {'emr_info': res}
    else:
        return {'emr_info': 'null'}


def emr_file_ana_dev(file_path, feed_type='json'):
    file_data = pd.read_csv(file_path)
    file_data = file_data.replace(['-Inf', 'Inf'], 'null')  # 把Inf等替换为null
    full_data = []
    keys = file_data.keys()
    emr_key = [k for k in keys if func_map.get(k)]
    base_key = [k for k in keys if k not in emr_key]

    for index, row in file_data.iterrows():
        if row['年份'] != 2015:
            # print type(row['年份'])
            continue
        tmp_data = {'base_info': {}, 'emr_info': {}}
        for k in base_key:
            if row[k] == row[k]:
                tmp_data['base_info'].update({k: row[k]})
        for k in emr_key:
            if row[k] == row[k]:
                tmp_data.update(emr_ana_dev(row[k], k))
        full_data.append(tmp_data)
    if feed_type == 'json':
        return json.dumps(full_data, ensure_ascii=False)
    else:
        return full_data


def list2list(query):
    full_data = []
    keys = query[0][1].keys()
    emr_key = [k for k in keys if func_map.get(k)]
    base_key = [k for k in keys if k not in emr_key]
    for index, row in query:
        tmp_data = {'base_info': {}, 'emr_info': {}}
        for k in base_key:
            if row[k] == row[k]:
                tmp_data['base_info'].update({k: row[k]})
        for k in emr_key:
            if row[k] == row[k]:
                tmp_data.update(emr_ana_dev(row[k], k))
        full_data.append(tmp_data)
        return full_data

