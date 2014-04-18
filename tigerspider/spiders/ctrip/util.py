#!/usr/bin/python2.7
#-*- coding=utf-8 -*-


"""universal toolkits for ctrip
    ALLIANCE_ID: alliance id for api of ctrip
    SID: sid code(one of authenticat)
    API_URL: url of api
    API_KEY: api key
    __city2code: cityname 2 citycode dict
    HOTEL_SERVICE_CODES: hotel service code in ctrip api
    is_needed_for_city: whether this city is needed
    build_hotel_url: build hotel url based on hotel code
    build_hotels_task_for_city: build HttpTask for hoteles description
    build_rooms_task_for_hotel: build HttpTask for room description
    convert_hotel_info_item_2_dict: convert hotel info item 2 dict
    convert_room_info_item_2_dict: convert room info item 2 dict
    get_city_code: get city code
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

import hashlib
import time
from xml.sax.saxutils import escape
from tornado.httpclient import HTTPRequest

from tigerspider.core.datastruct import HttpTask
from tigerspider.core.util import get_project_path

#(fake alliance id)
ALLIANCE_ID = 543534
# (fake sid code)
SID = 43535
API_URL = "openapi.ctrip.com"
# (fake api key)
API_KEY = "823436C3-DEDE-4F3C-B20B-9CA6C2BC7BD"

# _chinese_city2code = {
#     u"北京": "110000",
#     u"长春": "220100",
#     u"长沙": "430100",
#     u"成都": "510100",
#     u"重庆": "500000",
#     u"大连": "210200",
#     u"东莞": "441900",
#     u"佛山": "440600",
#     u"福州": "350100",
#     u"广州": "440100",
#     u"贵阳": "520100",
#     u"哈尔滨": "230100",
#     u"海口": "460100",
#     u"杭州": "330100",
#     u"合肥": "340100",
#     u"呼和浩特": "150100",
#     u"济南": "370100",
#     u"昆明": "530100",
#     u"兰州": "620100",
#     u"南昌": "360100",
#     u"南京": "320100",
#     u"南宁": "450100",
#     u"宁波": "330200",
#     u"青岛": "370200",
#     u"上海": "310000",
#     u"汕头": "440500",
#     u"沈阳": "210100",
#     u"深圳": "440300",
#     u"石家庄": "130100",
#     u"苏州": "320500",
#     u"太原": "140100",
#     u"天津": "120000",
#     u"温州": "330300",
#     u"武汉": "420100",
#     u"乌鲁木齐": "650100",
#     u"无锡": "320200",
#     u"厦门": "350200",
#     u"西安": "610100",
#     u"扬州": "321000",
#     u"烟台": "370600",
#     u"郑州": "410100",
#     u"珠海": "440400",
#     u"惠州": "441300",
# }
#
# _city2code = {
#     "beijing": "110000",
#     "all": "000000",
#     "changchun": "220100",
#     "changsha": "430100",
#     "chengdu": "510100",
#     "chongqing": "500000",
#     "dalian": "210200",
#     "dongguan": "441900",
#     "foshan": "440600",
#     "fuzhou": "350100",
#     "guangzhou": "440100",
#     "guiyang": "520100",
#     "haerbin": "230100",
#     "haikou": "460100",
#     "hangzhou": "330100",
#     "hefei": "340100",
#     "huhehaote": "150100",
#     "jinan": "370100",
#     "kunming": "530100",
#     "lanzhou": "620100",
#     "nanchang": "360100",
#     "nanjing": "320100",
#     "nanning": "450100",
#     "ningbo": "330200",
#     "qingdao": "370200",
#     "shanghai": "310000",
#     "shantou": "440500",
#     "shenyang": "210100",
#     "shenzhen": "440300",
#     "shijiazhuang": "130100",
#     "suzhou": "320500",
#     "taiyuan": "140100",
#     "tianjin": "120000",
#     "wenzhou": "330300",
#     "wuhan": "420100",
#     "wulumuqi": "650100",
#     "wuxi": "320200",
#     "xiamen": "350200",
#     "xian": "610100",
#     "yangzhou": "321000",
#     "yantai": "370600",
#     "zhengzhou": "410100",
#     "zhuhai": "440400",
#     "huizhou": "441300",
# }

HOTEL_SERVICE_CODES = ('9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
                       '38', '39', '40', '41',
                       '55',
                       '57', '58', '59', '60',
                       '69',
                       '99', '100', '101', '102',
                       '105')

ROOM_SERVICE_CODES = ('75', '76', '77', '78', '79', '80', '81', '82', '83', '84',
                      '86', '87', '88', '89', '90', '91', '92', '93', '94', '95', '96', '97', '98',
                      '103', '104',
                      '106', '107', '108', '109', '110', '111', '112', '113', '114', '115')

# def is_needed_for_city(english_name, chinese_name):
#     """whether this city is needed
#
#         Args:
#             english_name: str, english name of city
#             chinese_name: str, chinese name of city
#         Returns:
#             is_needed: bool, whether is needed
#     """
#     lower = english_name.lower()
#     if _city2code.has_key(lower) and _chinese_city2code.has_key(chinese_name)\
#         and _city2code.get(lower) == _chinese_city2code.get(chinese_name):
#         print english_name, chinese_name
#         return True
#     else:
#         return False
#
_city2code = dict()


def read_city_codes_from_file():
    """read city code files into dict
    """
    city_code_file_path = "%s%s" % (get_project_path(), "city_code.csv")

    with open(city_code_file_path, "rb") as in_file:
        for line in in_file:
            _, chinese, city_code = line.split(",")
            _city2code[chinese] = city_code.strip()


def get_city_code(chinese_name):
    """get city code

        Args:
             chinese_name: str, chinese name for city
        Returns:
             city_code: str, city code for city
    """
    if not hasattr(read_city_codes_from_file, "hasbeenread"):
        read_city_codes_from_file()
        setattr(read_city_codes_from_file, "hasbeenread", True)
    return _city2code.get(chinese_name.encode("utf-8"), None)


def _create_signature(timestamp, alliance, sid, request_type, api_key):
    """create signature for ctrip

        Args:
            timestamp: int, timestamp
            alliance: str, alliance id
            sid: str, sid
            request_type: str, request type
            api_key: str, api key
    """
    m = hashlib.md5()
    m.update(str(timestamp))
    m.update(str(alliance))
    m.update(hashlib.new("md5", str(api_key)).hexdigest().upper())
    m.update(str(sid))
    m.update(str(request_type))
    return m.hexdigest().upper()


def build_hotels_task_for_city(ctrip_code, city_code, chinese_name, avaliable="false"):
    """build task for hotel search

        Args:
            ctrip_code: str, city code for ctrip
            city_code: str, city code of tigerknows
            chinese_name: str, chinese name of city
        Returns:
            task: HttpTask, new task
    """
    timestamp = int(time.time())
    request_xml = """<?xml version="1.0" encoding="utf-8"?>
    <Request><Header  AllianceID="%s" SID="%s" TimeStamp="%s"
     RequestType="%s" Signature="%s" /><HotelRequest>
    <RequestBody xmlns:ns="http://www.opentravel.org/OTA/2003/05"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <ns:OTA_HotelSearchRQ Version="1.0" PrimaryLangID="zh"
    xsi:schemaLocation="http://www.opentravel.org/OTA/2003/05 OTA_HotelSearchRQ.xsd"
    xmlns="http://www.opentravel.org/OTA/2003/05">
    <ns:Criteria AvailableOnlyIndicator="%s"><ns:Criterion>
    <ns:HotelRef HotelCityCode="%s"/>
    <ns:Position PositionTypeCode="502" />
    </ns:Criterion></ns:Criteria></ns:OTA_HotelSearchRQ>
    </RequestBody></HotelRequest></Request>""" \
    % (ALLIANCE_ID, SID, timestamp, "OTA_HotelSearch",
       _create_signature(timestamp, ALLIANCE_ID, SID, "OTA_HotelSearch", API_KEY),
       avaliable, ctrip_code,)

    post_xml = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body><Request xmlns="http://ctrip.com/">
    <requestXML>%s</requestXML></Request></soap:Body></soap:Envelope>""" \
               % escape(request_xml)

    http_request = HTTPRequest("http://%s/Hotel/OTA_HotelSearch.asmx" % API_URL, method="POST",
                               body=post_xml, connect_timeout=20, request_timeout=240,
                               headers={"SOAPAction": "http://ctrip.com/Request",
                                        "Content-Type": "text/xml; charset=utf-8"})

    return HttpTask(http_request, callback="HotelListParser", max_fail_count=5,
                    kwargs={"citycode": city_code, "chinesename": chinese_name})


def build_rooms_task_for_hotel(hotel_requests, city_code, chinese_name, hotel_addresses):
    """build room task for hotel

        Args:
            hotel_requests: list, [(hotel_code, city_code, chinese_name)]
            city_code: str, city code of tigerknows
            chinese_name: str, chinese name of city
            hotel_addresses: dict, hotel address dict
        Returns:
            task: HttpTask, new task for hotel search
    """
    timestamp = int(time.time())

    request_info_xml = "".join(["""<HotelDescriptiveInfo HotelCode="%s" PositionTypeCode="502">
    <HotelInfo SendData="true"/><FacilityInfo SendGuestRooms="true"/>
    <AreaInfo SendAttractions="false" SendRecreations="false"/>
    <ContactInfo SendData="false"/><MultimediaObjects SendData="true"/>
    </HotelDescriptiveInfo>""" % hotel_code for hotel_code in hotel_requests])

    request_xml = """<?xml version="1.0" encoding="utf-8"?><Request>
    <Header  AllianceID="%s" SID="%s" TimeStamp="%s"  RequestType="%s" Signature="%s" />
    <HotelRequest><RequestBody xmlns:ns="http://www.opentravel.org/OTA/2003/05"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <OTA_HotelDescriptiveInfoRQ Version="1.0"
    xsi:schemaLocation="http://www.opentravel.org/OTA/2003/05
    OTA_HotelDescriptiveInfoRQ.xsd" xmlns="http://www.opentravel.org/OTA/2003/05"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <HotelDescriptiveInfos>%s</HotelDescriptiveInfos></OTA_HotelDescriptiveInfoRQ>
    </RequestBody></HotelRequest></Request>""" % (
        ALLIANCE_ID, SID, timestamp, "OTA_HotelDescriptiveInfo",
        _create_signature(timestamp, ALLIANCE_ID, SID, "OTA_HotelDescriptiveInfo", API_KEY), request_info_xml)

    post_xml = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema"
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body><Request xmlns="http://ctrip.com/">
    <requestXML>%s</requestXML></Request></soap:Body></soap:Envelope>""" \
               % escape(request_xml)

    http_request = HTTPRequest("http://%s/Hotel/OTA_HotelDescriptiveInfo.asmx" % API_URL,
                               method="POST", body=post_xml, connect_timeout=20, request_timeout=360,
                               headers={"SOAPAction": "http://ctrip.com/Request",
                                        "Content-Type": "text/xml; charset=utf-8"})
    return HttpTask(http_request, callback="HotelParser", max_fail_count=5,
                    kwargs={"citycode": city_code, "chinesename": chinese_name,
                            "address": hotel_addresses})


def build_hotel_url(hotel_id):
    """build hotel url

        Args:
            hotel_id: str, hotel code
        Returns:
            hotel_url: str, hotel url
    """
    return "http://hotels.ctrip.com/hotel/%s.html" % hotel_id


def convert_room_info_item_2_dict(room_info_item):
    """convert room info item 2 dict

        Args:
            room_info_item: RoomInfoItem, item of room info
        Returns:
            room_dict: Dict, dict of room info
    """
    room_dict = {
        # "hotel_id": room_info_item.hotel_code,
        "room_id": room_info_item.room_id,
        "room_type": room_info_item.room_type,
        "floor": room_info_item.floor,
        "net_service": room_info_item.net_service,
        "net_service_fee": room_info_item.net_service_fee,
        "bed_type": room_info_item.bed_type,
        "breakfast": room_info_item.breakfast,
        "area": room_info_item.area,
    }
    return room_dict


def convert_hotel_info_item_2_dict(hotel_info_item):
    """convert hotel info item 2 dict

        Args:
            hotel_info_item: HotelInfoItem, item
        Returns:
            hotel_dict: dict
    """
    preview = hotel_info_item.hotel_preview if not isinstance(
        hotel_info_item.hotel_preview, unicode) else \
        hotel_info_item.hotel_preview.encode("utf-8")

    hotel_service = hotel_info_item.hotel_services if not isinstance(
        hotel_info_item.hotel_services, unicode) else \
        hotel_info_item.hotel_services.encode("utf-8")

    room_service = hotel_info_item.room_services if not isinstance(
        hotel_info_item.room_services, unicode) else \
        hotel_info_item.room_services.encode("utf-8")

    hotel_name = hotel_info_item.hotel_name if not isinstance(
        hotel_info_item.hotel_name, unicode) else \
        hotel_info_item.hotel_name.encode("utf-8")

    hotel_dict = {
        "hotel_id": hotel_info_item.hotel_code,
        "city_code": hotel_info_item.city_code,
        "hotel_name": hotel_name,
        "brand_id": hotel_info_item.brand_id,
        "latitude": hotel_info_item.latitude,
        "longitude": hotel_info_item.longitude,
        "hotel_service": hotel_service,
        "room_service": room_service,
        "hotel_star": hotel_info_item.hotel_star,
        "hotel_rate": hotel_info_item.hotel_rate,
        "images": hotel_info_item.image_list,
        "preview": preview,
        "rooms": hotel_info_item.room_list,
        "address": hotel_info_item.address,
    }
    return hotel_dict