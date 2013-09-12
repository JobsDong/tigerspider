#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import datetime

from core.util import remove_white

_city2code = {
    "beijing": "110000",
    "all": "000000",
    "changchun": "220100",
    "changsha": "430100",
    "chengdu": "510100",
    "chongqing": "500000",
    "dalian": "210200",
    "dongguan": "441900",
    "foshan": "440600",
    "fuzhou": "350100",
    "guangzhou": "440100",
    "guiyang": "520100",
    "haerbin": "230100",
    "haikou": "460100",
    "hangzhou": "330100",
    "hefei": "340100",
    "huhehaote": "150100",
    "jinan": "370100",
    "kunming": "530100",
    "lanzhou": "620100",
    "nanchang": "360100",
    "nanjing": "320100",
    "nanning": "450100",
    "ningbo": "330200",
    "qingdao": "370200",
    "shanghai": "310000",
    "shantou": "440500",
    "shenyang": "210100",
    "shenzhen": "440300",
    "shijiazhuang": "130100",
    "suzhou": "320500",
    "taiyuan": "140100",
    "tianjin": "120000",
    "wenzhou": "330300",
    "wuhan": "420100",
    "wulumuqi": "650100",
    "wuxi": "320200",
    "xiamen": "350200",
    "xian": "610100",
    "yangzhou": "321000",
    "yantai": "370600",
    "zhengzhou": "410100",
    "zhuhai": "440400",
    "huizhou": "441300",
}

_mt2tiger = {
    u"KTV": u"KTV",

    u"电影院": u"电影",

    u"国内游":u"酒店旅游",
    u"四星级/高档":u"酒店旅游",
    u"经济型/客栈":u"酒店旅游",
    u"一星级":u"酒店旅游",
    u"五星级/豪华":u"酒店旅游",
    u"三星级":u"酒店旅游",
    u"二星级":u"酒店旅游",

    u"美发":u"丽人",
    u"美甲/手护":u"丽人",
    u"SPA/美容/美体":u"丽人",
    u"脱毛/塑身/整容":u"丽人",
    u"化妆":u"丽人",
    u"其他丽人":u"丽人",
    u"婚纱摄影":u"丽人",
    u"个性写真":u"丽人",

    u"其他自助":u"美食",
    u"海鲜":u"美食",
    u"小吃":u"美食",
    u"快餐":u"美食",
    u"蛋糕":u"美食",
    u"咖啡厅/酒吧/茶室":u"美食",
    u"素食":u"美食",
    u"日本菜":u"美食",
    u"韩国菜":u"美食",
    u"东南亚菜":u"美食",
    u"江浙菜":u"美食",
    u"港式/粤菜":u"美食",
    u"其他中餐":u"美食",
    u"麻辣烫/串串香":u"美食",
    u"西餐":u"美食",
    u"川湘菜/湖北菜":u"美食",
    u"海鲜自助":u"美食",
    u"日料自助":u"美食",
    u"烤肉自助":u"美食",
    u"披萨自助":u"美食",
    u"综合类自助":u"美食",
    u"西北菜":u"美食",
    u"东北菜":u"美食",
    u"北京菜/鲁菜":u"美食",
    u"云贵菜":u"美食",
    u"干锅/烤鱼":u"美食",
    u"饮品/甜品/甜点":u"美食",
    u"披萨":u"美食",
    u"中亚菜/中东菜":u"美食",
    u"其他异国餐饮":u"美食",
    u"其他餐饮":u"美食",
    u"自助火锅":u"美食",
    u"清真菜":u"美食",
    u"中式烧烤/烤串":u"美食",
    u"客家/台湾":u"美食",
    u"汤/煲/砂锅/粥/炖菜":u"美食",
    u"创意菜/特色菜":u"美食",
    u"家常菜/农家菜/综合类":u"美食",
    u"火锅":u"美食",

    u"体检":u"生活服务",
    u"齿科":u"生活服务",
    u"艺术培训课程":u"生活服务",
    u"其他培训课程":"生活服务",
    u"儿童写真":u"生活服务",
    u"照片冲印/快印":u"生活服务",
    u"租车":u"生活服务",
    u"加油站":u"生活服务",
    u"汽车保养":u"生活服务",
    u"报刊杂志订阅":u"生活服务",
    u"充值服务":u"生活服务",
    u"宠物服务":u"生活服务",
    u"服装定制":u"生活服务",
    u"家政服务":u"生活服务",
    u"衣物/皮具洗护":u"生活服务",
    u"鲜花":u"生活服务",
    u"婚庆服务":u"生活服务",
    u"其他生活服务":u"生活服务",
    u"配镜服务":u"生活服务",
    u"母婴服务":u"生活服务",
    u"语言培训课程":u"生活服务",
    u"本地购物":u"生活服务",
    u"早教/儿童课程":u"生活服务",
    u"职业培训课程":u"生活服务",
    u"驾校":u"生活服务",
    u"网球/壁球":u"生活服务",
    u"武术":u"生活服务",
    u"其他文化艺术":u"生活服务",
    u"证件照":u"生活服务",
    u"其他摄影":u"生活服务",

    u"保健/按摩":u"休闲娱乐",
    u"桌面游戏":u"休闲娱乐",
    u"电玩/游戏币":"休闲娱乐",
    u"DIY(陶艺/巧克力/蛋糕/蜡烛)":u"休闲娱乐",
    u"真人CS":u"休闲娱乐",
    u"采摘/钓鱼/自助烧烤":u"休闲娱乐",
    u"动物园/海洋馆/植物园":u"休闲娱乐",
    u"主题公园/游乐园":u"休闲娱乐",
    u"儿童乐园":u"休闲娱乐",
    u"景点":u"休闲娱乐",
    u"水上乐园":u"休闲娱乐",
    u"温泉/洗浴/汗蒸":u"休闲娱乐",
    u"博物馆/美术馆/科技馆":u"休闲娱乐",
    u"展览":u"休闲娱乐",
    u"高空观景":u"休闲娱乐",
    u"单车游/巴士游/游船":u"休闲娱乐",
    u"演唱会":u"休闲娱乐",
    u"体育赛事":u"休闲娱乐",
    u"健身房":u"休闲娱乐",
    u"瑜伽/普拉提/健身操/形体":u"休闲娱乐",
    u"高尔夫":u"休闲娱乐",
    u"保龄球":u"休闲娱乐",
    u"台球":u"休闲娱乐",
    u"羽毛球/乒乓球":u"休闲娱乐",
    u"射箭/射击":u"休闲娱乐",
    u"赛车":u"休闲娱乐",
    u"骑马":u"休闲娱乐",
    u"攀登运动":u"休闲娱乐",
    u"游泳/水上运动":u"休闲娱乐",
    u"滑雪/滑冰":u"休闲娱乐",
    u"篮球/足球":u"休闲娱乐",
    u"其他运动":u"休闲娱乐",
    u"其他休闲娱乐":u"休闲娱乐",
    u"相声":u"休闲娱乐",
    u"其他剧目":u"休闲娱乐",
    u"足疗":u"休闲娱乐",
    u"儿童剧":u"休闲娱乐",
    u"话剧":u"休闲娱乐",
    u"歌舞剧":u"休闲娱乐",
    u"传统戏剧":u"休闲娱乐",
    u"音乐会":u"休闲娱乐",
    u"点播式电影":u"休闲娱乐",
    u"4D/5D电影":u"休闲娱乐",
    u"密室逃脱":u"休闲娱乐",
}

def get_city_code(city_pname):
    """获得对应城市的code
        Args:
            city_pname: str, 城市英文名字
        Returns:
            code: str, 如果不存在就返回None
    """
    return None if not _city2code.has_key(city_pname) else _city2code[city_pname]

def get_subcate_by_category(category):
    """将meituan分类映射到对应的类别
        Args:
            category: str, 类别
        Returns:
            subcate: str, 类别,如果不存在就返回None
    """
    return None if not _mt2tiger.has_key(category) else _mt2tiger[category]

def build_url_by_city_name(city_qname):
    """根据city_name构建对应的api host
        Args:
            city_qname: str, 城市英文名
        Returns:
            url: str, host
    """
    return "http://www.meituan.com/api/v2/%s/deals" % city_qname

def extract_table(elem, text_splits):
    """解析table标签的内容
        Args:
            elem: Element, 节点元素
    """
    if elem is not None:
        tr_elems = elem.xpath("tr")
        for tr_elem in tr_elems:
            text_splits.append(u"-")
            for text in tr_elem.itertext():
                stripped_text = remove_white(text)
                if len(stripped_text) > 0:
                    text_splits.append(u" " + stripped_text)
            text_splits.append(u"N_line")

def extract_deal_menu_summary(elem, text_splits):
    if elem is not None:
        text_splits.append(u"-")
        for text in elem.itertext():
            stripped_text = remove_white(text)
            if len(stripped_text) > 0:
                text_splits.append(u" " + stripped_text)
        text_splits.append(u"N_line")

def extract_room_status_w(elem, text_splits):
    if elem is not None:
        room_status_elems = elem.xpath("div[@class='room-status']//ul[@class='room-status__hint']")
        for room_status in room_status_elems:
            extract_list(room_status, text_splits)

def extract_list(elem, text_splits):
    if elem is not None:
        for li_elem in elem:
            temps = []
            for text in li_elem.itertext():
                stripped_text = remove_white(text)
                if len(stripped_text) > 0:
                    temps.append(u" " + stripped_text)
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
        if key is "start_time":
            clone_dict['start_time'] = datetime.datetime.fromtimestamp(
            float(value)).strftime("%Y-%m-%d %H:%M:%S")
        elif key is "end_time":
            clone_dict['end_time'] = datetime.datetime.fromtimestamp(
            float(value)).strftime("%Y-%m-%d %H:%M:%S")
        elif key is "deadline":
            clone_dict['deadline'] = datetime.datetime.fromtimestamp(
            float(value)).strftime("%Y-%m-%d %H:%M:%S")
        elif key is "pictures":
            clone_dict['pictures'] = [child_value if not isinstance(child_value, unicode)
                                    else child_value.encode("utf-8")
                                    for child_value in value]
        elif key is "place":
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