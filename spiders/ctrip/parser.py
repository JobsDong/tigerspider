#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

"""parser for ctrip
    CityParser: parser of city
    HotelListParser: parser for hotel list
    HotelParser: parser for hotel infomation
"""

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from lxml import etree

from core.spider.parser import BaseParser
from core.util import remove_white, xpath_namespace, flist
from core.spider.parser import ParserError

from spiders.ctrip.util import (HOTEL_SERVICE_CODES,ROOM_SERVICE_CODES,
                                build_hotels_task_for_city,build_rooms_task_for_hotel,
                                build_hotel_url)
from spiders.ctrip.items import (CityItem, RoomInfoItem,
                                 HotelInfoItem, HotelCodeItem,
                                 ImageItem)

class CityParser(BaseParser):
    """parse city xml
    """

    def parse(self, task, input_file):
        """parse city xml file
            Args:
                task: HttpTask or FileTask,
                input_file: file, response body or file
            Yields:
                item: Item, result of parse
                task: Task, new task
        """
        self.logger.debug("city parser begin to parse")
        try:
            tree = etree.parse(input_file)

            elems = tree.xpath("//CityDetail")
            for elem in elems:
                chinese_name = remove_white(elem.findtext("CityName", ""))
                city_code = remove_white(elem.findtext("CityCode", ""))
                ctrip_code = remove_white(elem.findtext("City", ""))

                if len(chinese_name) <= 0 or len(city_code) <= 0 or len(ctrip_code) <= 0:
                    self.logger.debug("invaliade city chinese_name:%s citycode:%s ctrip_code:%s"
                                      % (chinese_name, city_code, ctrip_code))
                    continue

                yield build_hotels_task_for_city(ctrip_code, city_code, chinese_name)
                yield CityItem(chinese_name, ctrip_code, city_code)

        except Exception, e:
            self.logger.error("city parser extract error:%s" % e)
        finally:
            self.logger.debug("city parser end to parse")


class HotelListParser(BaseParser):
    """parse hotel result
    """

    def __init__(self, namespace, batch_count=50):
        BaseParser.__init__(self, namespace)
        self.logger.debug("init HotelListParser")
        self.batch_count = batch_count

    def parse(self, task, input_file):
        """parse response result

            Args:
                task: FileTask or HttpTask
                input_file: file or StringIO
            Yields:
                item: Item, result of parse
                task: Task, new task
        """
        self.logger.debug("hotel parser begin to parse")
        try:
            soap_tree = etree.fromstring(input_file.read())
            soap_elems = xpath_namespace(soap_tree,
                            "/soap:Envelope/soap:Body/RequestResponse/RequestResult")
            xml_str = soap_elems[0].text
            tree = etree.fromstring(xml_str)
            elems = tree.xpath("/Response/Header")
            header = elems[0]
            if header.attrib.has_key("ResultCode") and header.attrib['ResultCode'] == "Success":
                # success
                property_elems = xpath_namespace(tree, "/Response/HotelResponse/OTA_HotelSearchRS/Properties/Property")
                city_code = task.kwargs.get('citycode')
                chinese_name = task.kwargs.get('chinesename')

                hotel_requests = list()
                hotel_addresses = dict()
                for property_elem in property_elems:
                    hotel_code = property_elem.attrib['HotelCode'] if property_elem.attrib.has_key('HotelCode') \
                        else None
                    hotel_ctrip_city_code = property_elem.attrib['HotelCityCode'] \
                        if property_elem.attrib.has_key('HotelCityCode') else None

                    hotel_address = flist(property_elem.xpath("*[local-name()='Address']/*[local-name()='AddressLine']/text()"))
                    if isinstance(hotel_address, unicode):
                        hotel_address = hotel_address.encode("utf-8")

                    if hotel_code and hotel_ctrip_city_code:
                        hotel_url = build_hotel_url(hotel_code)
                        yield HotelCodeItem(hotel_code, city_code, hotel_url)

                        hotel_requests.append(hotel_code)
                        hotel_addresses[hotel_code] = hotel_address
                        if len(hotel_requests) >= self.batch_count:
                            yield build_rooms_task_for_hotel(hotel_requests, city_code, chinese_name, hotel_addresses)
                            hotel_addresses.clear()
                            del hotel_requests[:]

                # send left requests
                if len(hotel_requests) > 0:
                    yield build_rooms_task_for_hotel(hotel_requests, city_code, chinese_name, hotel_addresses)
                    hotel_addresses.clear()
                    del hotel_requests[:]
        finally:
            self.logger.debug("hotel parse end to parse")


class HotelParser(BaseParser):
    """parse hotel description
    """

    def parse(self, task, input_file):
        """parse method

            Args:
                task: Task, task
                input_file: file: file with content
            Yields:
                item: Item, result of parse
                task: Task, new task
        """
        self.logger.debug("room parser begin to parse")
        try:
            try:
                soap_tree = etree.fromstring(input_file.read())
            except Exception, e:
                self.logger.error("not complete xml:%s" % e)
                raise ParserError("not complete xml")

            hotel_address_dict = task.kwargs.get('address')
            soap_elems = xpath_namespace(soap_tree,
                            "/soap:Envelope/soap:Body/RequestResponse/RequestResult")
            xml_str = soap_elems[0].text

            tree = etree.fromstring(xml_str)
            elems = tree.xpath("/Response/Header")
            header = elems[0]

            if not header.attrib.has_key("ResultCode") or header.attrib['ResultCode'] != "Success":
                self.logger.error("not has resultcode or resultcode is not success")
                raise ParserError("ResultCode error")
            else:
                content_elems = xpath_namespace(tree,
                                "/Response/HotelResponse/OTA_HotelDescriptiveInfoRS/"
                                "HotelDescriptiveContents/HotelDescriptiveContent")
                for content_elem in content_elems:
                    item_hotel_code = None
                    item_hotel_city_code = task.kwargs.get('citycode')
                    try:
                        item_hotel_code = content_elem.attrib.get('HotelCode')
                        # item_hotel_city_ctrip = content_elem.attrib.get("HotelCityCode")
                        item_hotel_name = content_elem.attrib.get('HotelName')
                        item_hotel_brand_id = content_elem.attrib.get('BrandCode')

                        position_elem = flist(xpath_namespace(content_elem, "HotelInfo//Position"), None)
                        item_hotel_latitude = "" if position_elem is None or not position_elem.attrib.has_key('Latitude') \
                            else position_elem.attrib.get('Latitude')
                        item_hotel_longitude = "" if position_elem is None or not  position_elem.attrib.has_key("Longitude") \
                            else position_elem.attrib.get('Longitude')

                        service_elems = xpath_namespace(content_elem, "HotelInfo/Services/Service")

                        item_hotel_service = u"、".join(
                            [flist(service.xpath("*[local-name()='DescriptiveText']/text()"))
                            for service in service_elems
                            if service.attrib.has_key("Code")
                            and service.attrib["Code"] in HOTEL_SERVICE_CODES])

                        item_room_service = u"、".join(
                            [flist(service.xpath("*[local-name()='DescriptiveText']/text()"))
                            for service in service_elems
                            if service.attrib.has_key("Code")
                            and service.attrib["Code"] in ROOM_SERVICE_CODES])

                        awards_elem = flist(xpath_namespace(content_elem, "AffiliationInfo/Awards"), None)
                        item_hotel_star, item_hotel_rate = ("", "") if awards_elem is None else \
                            (flist(awards_elem.xpath("*[local-name()='Award' and @Provider='HotelStarRate']/@Rating")),
                            flist(awards_elem.xpath("*[local-name()='Award' and @Provider='CtripStarRate']/@Rating")))

                        multimedia_elem = flist(xpath_namespace(content_elem, "MultimediaDescriptions"), None)
                        image_elems = [] if multimedia_elem is None else xpath_namespace(multimedia_elem,
                                          "MultimediaDescription/ImageItems/ImageItem")

                        item_image_list = []
                        for image_elem in image_elems:
                            image_url = flist(image_elem.xpath(
                                "*[local-name()='ImageFormat']/*[local-name()='URL']/text()"))
                            image_type = flist(image_elem.xpath("@Category"))
                            if not image_url and not image_type:
                                continue
                            image_text = flist(image_elem.xpath("*[local-name()='Description']/@Caption"))
                            item_image_dict = {"image_url": image_url,
                                   "image_type": image_type,
                                   "image_text": image_text.encode('utf-8')}
                            item_image_list.append(item_image_dict)

                            if item_hotel_code and image_url:
                                image_item = ImageItem(item_hotel_code, image_type, image_text, image_url)
                                yield image_item

                        text_items_elem = flist(xpath_namespace(
                            multimedia_elem, "MultimediaDescription/TextItems"), None)
                        item_hotel_preview = "" if text_items_elem is None else flist(text_items_elem.xpath(
                            "*[local-name()='TextItem' and @Category='5']/*[local-name()='Description']/text()"))

                        room_elems = xpath_namespace(content_elem, "FacilityInfo/GuestRooms/GuestRoom")
                        item_room_list = []
                        for room_elem in room_elems:
                            room_info_id = flist(room_elem.xpath("*[local-name()='TypeRoom']/@RoomTypeCode"))
                            room_info_name = flist(room_elem.xpath("@RoomTypeName"))
                            room_bed_type = flist(room_elem.xpath("*[local-name()='TypeRoom']/@BedTypeCode"))
                            room_net_service, room_net_service_fee = self._extract_net_service(room_elem)
                            room_info_rate_price = ""
                            room_hot = ""
                            room_floor = flist(room_elem.xpath("*[local-name()='TypeRoom']/@Floor"))
                            room_breakfast = ""
                            room_area = ""
                            room_info_dict = {'roomInfo_id': room_info_id,
                                      'roomInfo_ratePrice': room_info_rate_price,
                                      'hot': room_hot}
                            if room_info_id and room_info_name and item_hotel_code:
                                item_room_list.append(room_info_dict)

                                room_item = RoomInfoItem(item_hotel_code, room_info_id, room_info_name,
                                            room_floor, room_net_service, room_net_service_fee,
                                            room_bed_type, room_breakfast, room_area)
                                yield room_item

                        item_hotel_address = "" if not hotel_address_dict.has_key(item_hotel_code) \
                            else  hotel_address_dict.get(item_hotel_code)
                        hotel_item = HotelInfoItem(item_hotel_code, item_hotel_city_code, item_hotel_name,
                                           item_hotel_brand_id, item_hotel_latitude, item_hotel_longitude,
                                           item_hotel_service, item_room_service, item_hotel_star, item_hotel_rate,
                                           item_image_list, item_hotel_preview, item_room_list, item_hotel_address)

                        yield hotel_item
                    except Exception, e:
                        self.logger.warn("one hotel extract error:%s" % e)
                        if item_hotel_code is None:
                            self.logger.error("i am sorry, i can do noting")
                        else:
                            chinese_name = task.kwargs.get('chinesename')
                            yield build_rooms_task_for_hotel([item_hotel_code], item_hotel_city_code, chinese_name)
        finally:
            self.logger.debug("room parser end to parse")

    def _extract_net_service(self, room_elem):
        """extract net service

            Args:
                room_elem: _Element
            Returns:
                net_service, service_fee: tuple, (str, str)
        """
        codes = room_elem.xpath("*[local-name()='Amenities']//*[local-name()='Amenity']"
                                "/@RoomAmenityCode")
        if "1" in codes or "3" in codes or "5" in codes:
            net_service = u"有"
            net_service_fee = u"免费"
        elif "2" in codes or "4" in codes or "6" in codes:
            net_service = u"有"
            net_service_fee = u"收费"
        else:
            net_service = u"无"
            net_service_fee = u"免费"
        return (net_service, net_service_fee)

