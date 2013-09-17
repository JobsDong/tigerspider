#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime

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

def get_city_code(city_pname):
    """获取对应城市的cityCode,同时起到了一定的过滤效果
        Args:
            city_pname: 城市英文名
        Returns:
            city_code: str, 城市id
    """
    return None if not _city2code.has_key(city_pname) else _city2code[city_pname]

def build_url_by_city_name(city_pname):
    """根据city的name构造出对应的url
        Args:
            city_pname: str, 城市名
        Returns:
            url: str, url
    """
    return "http://www.nuomi.com/api/tiger?city=%s" % city_pname

def get_subcate_by_category(category):
    """将糯米网的类别映射到tiger的类别
        Args:
            category: str, 类别名
        Returns:
            subcate: str, 如果不是需要的就返回None
    """
    if category.rfind(u"教育培训") != -1:
        return None
    elif category.rfind(u"生活服务-其他 生活服务-美发") != -1:
        return u"丽人"
    elif category.rfind(u"生活服务-其他 生活服务-美甲") != -1:
        return u"丽人"
    elif category.rfind(u"生活服务-其他 生活服务-SPA/美容美体") != -1:
        return u"丽人"
    elif category.rfind(u"生活服务-亲子 生活服务-婚纱摄影 生活服务-摄影写真 生活服务-儿童摄影 生活服务-婚庆服务") != -1:
        return u"丽人"
    elif category.rfind(u"生活服务-摄影写真 生活服务-快照冲印") != -1:
        return u"生活服务"
    elif category.rfind(u"生活服务-亲子 生活服务-摄影写真 生活服务-儿童摄影") != -1:
        return u"生活服务"
    elif category.rfind(u"生活服务-摄影写真 生活服务-儿童摄影") != -1:
        return u"生活服务"
    elif category.rfind(u"休闲娱乐-KTV 休闲娱乐-酒吧") != -1:
        return u"休闲娱乐"
    elif category.startswith(u"美食"):
        return u"美食"
    elif category.rfind(u"电影") != -1:
        return u"电影"
    elif category.startswith(u"酒店旅游"):
        return u"酒店旅游"
    elif category.rfind(u"摄影写真") != -1 or category.rfind(u"美发") != -1 or \
        category.rfind(u"SPA") != -1 or category.rfind(u"美容塑形") != -1 or \
        category.rfind(u"美甲") != -1:
        return u"丽人"
    elif category.rfind(u"KTV") != -1:
        return u"KTV"
    elif category.startswith(u"休闲娱乐") or category.rfind(u"养生保健") != -1 or \
        category.rfind(u"足疗按摩") != -1:
        return u"休闲娱乐"
    elif category.startswith(u"生活服务") or category.rfind(u"美容保健") != -1:
        return u"生活服务"
    else:
        return None

def item2dict(item):
    """讲item转换层dict
        Args:
            item:Item, item对象
        Returns:
            clone_dict:dict, 字典
    """
    clone_dict = {}
    for key, value in item.__dict__.items():
        if key == "pictures":
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
