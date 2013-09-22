#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""用于窝窝团购中的工具模块
    get_city_code(): 获取对应city的code值，另附加过滤效果
    build_url_by_city_name():拼接处城市api获取的url
    get_subcate_by_category():映射对应的分类
    extract_id_from_url():从url中提取出id值
    convert_to_m_url():将url转化成m_url
    extract_list(): 解析list
"""

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime

from core.util import remove_white

_city2code = {
"beijing":"110000",
"changchun":"220100",
"changsha":"430100",
"chengdu":"510100",
"chongqing":"500000",
"dalian":"210200",
"dongguan":"441900",
"foshan":"440600",
"fuzhou":"350100",
"guangzhou":"440100",
"guiyang":"520100",
"haerbin":"230100",
"haikou":"460100",
"hangzhou":"330100",
"hefei":"340100",
"huhehaote":"150100",
"jinan":"370100",
"kunming":"530100",
"lanzhou":"620100",
"nanchang":"360100",
"nanjing":"320100",
"nanning":"450100",
"ningbo":"330200",
"qingdao":"370200",
"shanghai":"310000",
"shenyang":"210100",
"shenzhen":"440300",
"shijiazhuang":"130100",
"suzhou":"320500",
"taiyuan":"140100",
"tianjin":"120000",
"wenzhou":"330300",
"wuhan":"420100",
"wulumuqi":"650100",
"wuxi":"320200",
"xiamen":"350200",
"xian":"610100",
"yangzhou":"321000",
"yantai":"370600",
"zhengzhou":"410100",
"zhuhai":"440400",
"huizhou":"441300",
}

#TODO 将功能进行分解
def get_city_code(city_pname):
    """获取对应城市的cityCode,同时起到了一定的过滤效果
        Args:
            city_pname: 城市英文名
        Returns:
            city_code: str, 城市id
    """
    return None if not _city2code.has_key(city_pname) else _city2code[city_pname]

def build_url_by_city_name(city_qname):
    return "http://www.55tuan.com/openAPI.do?city=%s" % city_qname

def get_subcate_by_category(category_texts):
    """
        notice: 结婚 is 丽人 ?
    """
    category = "".join(category_texts)
    if category.rfind(u"美食") != -1:
        return u"美食"
    elif category.rfind(u"教育培训") != -1:
        return None
    elif category.rfind(u"电影") != -1:
        return u"电影"
    elif category.rfind(u"旅行") != -1 or category.rfind(u"酒店") != -1:
        return u"酒店旅游"
    elif category.rfind(u"摄影写真") != -1 or category.rfind(u"美发") != -1 or \
    category.rfind(u"SPA") != -1 or category.rfind(u"美容塑形") != -1 or \
    category.rfind(u"美甲") != -1 or category.rfind(u'结婚') != -1:
        return u"丽人"
    elif category.rfind(u"KTV") != -1:
        return u"KTV"
    elif category.rfind(u"娱乐") != -1 or category.rfind(u"养生保健") != -1 or \
        category.rfind(u"足疗按摩") != -1:
        return u"休闲娱乐"
    elif category.rfind(u"生活服务") != -1 or category.rfind(u"美容保健") != -1:
        return u"生活服务"
    else:
        print category
        return None

def extract_id_from_url(url):
    """从url中解析出id
        Args:
            url: str, url
        Returns:
            id: str, id号
    """
    try:
        start, end = url.rindex("goods-"), url.rindex(".html")
    except ValueError:
        return None
    else:
        return url[start + 6:end]

def convert_to_m_url(url):
    dot = url.index(".55tuan")
    return "http://m" + url[dot:]

def extract_dl(elem, text_splits):
    """解析dl标签中的数据
        elem: Element, 节点元素
        text_splits: list, 是字符串数组，
    """
    if elem is not None:
        for dl_elem in elem:
            for text in dl_elem.itertext():
                striped_text = remove_white(text)
                if len(striped_text) > 0:
                    text_splits.append(striped_text)
                    text_splits.append("N_line")

def extract_table(elem, text_splits):
    if elem is not None:
        tr_elems = elem.xpath("//tr")
        for tr_elem in tr_elems:
            text_splits.append(u"-")
            temp_texts = []
            for text in tr_elem.itertext():
                stripped_text = remove_white(text)
                if len(stripped_text) > 0:
                    temp_texts.append(u" " + stripped_text)
            if len(temp_texts) > 0:
                text_splits.append(u"-")
                text_splits.extend(temp_texts)
                text_splits.append("N_line")

def extract_list(elem, text_splits):
    if elem is not None:
        for li_elem in elem:
            temps = []
            for text in li_elem.itertext():
                stripped_text = remove_white(text)
                if len(stripped_text) > 0:
                    temps.append(" " + stripped_text)
            if len(temps) > 0:
                text_splits.append(u"-")
                text_splits.extend(temps)
                text_splits.append(u"N_line")

def item2dict(item):
    """讲item转换层dict
        Args:
            item:Item, item对象
        Returns:
            clone_dict:dict, 字典
    """
    clone_dict = {}
    for key, value in item.__dict__.items():
        if key == "start_time":
            clone_dict['start_time'] = datetime.datetime.fromtimestamp(
            float(value)).strftime("%Y-%m-%d %H:%M:%S")
        elif key == "end_time":
            clone_dict['end_time'] = datetime.datetime.fromtimestamp(
            float(value)).strftime("%Y-%m-%d %H:%M:%S")
        elif key == "pictures":
            clone_dict['pictures'] = [child_value if not isinstance(child_value, unicode)
                                    else child_value.encode("utf-8")
                                    for child_value in value]
        elif key == "place":
            temp_value = []
            for place_value in value:
                temp_dict = {}
                for child_key, child_value in place_value.items():
                    if isinstance(child_value, unicode):
                        child_value = child_value.encode("utf-8")
                    if isinstance(child_key, unicode):
                        child_key = child_key.encode("utf-8")
                    temp_dict[child_key] = child_value
                temp_value.append(temp_dict)
            clone_dict['place'] = temp_value
        else:
            clone_dict[key] = value if not isinstance(value, unicode) \
                else value.encode("utf-8")

    return clone_dict
