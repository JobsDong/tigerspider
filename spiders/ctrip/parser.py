#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from lxml import etree

from core.spider.parser import BaseParser
from core.util import remove_white, xpath_namespace
from core.spider.parser import ParserError

from spiders.ctrip.util import (is_needed_for_city,HOTEL_SERVICE_CODES,
                                ROOM_SERVICE_CODES,get_city_code,
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
        """
        self.logger.debug("city parser begin to parse")
        try:
            tree = etree.parse(input_file)

            elems = tree.xpath("//CityDetail")
            for elem in elems:
                chinese_name = remove_white(elem.findtext("CityName"))
                english_name = remove_white(elem.findtext("CityEName"))
                ctrip_code = remove_white(elem.findtext("City"))

                if len(chinese_name) <= 0 or len(english_name) <= 0 or len(ctrip_code) <= 0:
                    self.logger.debug("invaliade city chinese_name:%s english_name:%s ctrip_code:%s"
                                      % (chinese_name, english_name, ctrip_code))
                    continue

                if not is_needed_for_city(english_name):
                    self.logger.debug("no need city english_name:%s" % english_name)
                    continue

                city_code = get_city_code(english_name)

                if city_code:
                    yield build_hotels_task_for_city(ctrip_code, city_code, chinese_name)
                    yield CityItem(chinese_name, english_name, ctrip_code, city_code)

        except Exception, e:
            self.logger.error("city parser extract error:%s" % e)
        finally:
            self.logger.debug("city parser end to parse")


class HotelListParser(BaseParser):
    """parse hotel result
    """
    BATCH_HOTEL_COUNT = 50

    def parse(self, task, input_file):
        """parse response result
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
                for property_elem in property_elems:
                    hotel_code = property_elem.attrib['HotelCode'] if property_elem.attrib.has_key('HotelCode') \
                        else None
                    hotel_ctrip_city_code = property_elem.attrib['HotelCityCode'] \
                        if property_elem.attrib.has_key('HotelCityCode') else None

                    if hotel_code and hotel_ctrip_city_code:
                        hotel_url = build_hotel_url(hotel_code)
                        print "hotel code:", hotel_code, hotel_url
                        yield HotelCodeItem(hotel_code, city_code, hotel_url)

                        if len(hotel_requests) <= self.BATCH_HOTEL_COUNT:
                            hotel_requests.append(hotel_code)
                        else:
                            print "requests:", len(hotel_requests)
                            yield build_rooms_task_for_hotel(hotel_requests, city_code, chinese_name)


                # send left requests
                if len(hotel_requests) > 0:
                    print "requests:", len(hotel_requests)
                    yield build_rooms_task_for_hotel(hotel_requests, city_code, chinese_name)
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
            soap_tree = etree.fromstring(input_file.read())
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
                    try:
                        item_hotel_code = content_elem.attrib.get('HotelCode')
                        # item_hotel_city_ctrip = content_elem.attrib.get("HotelCityCode")
                        item_hotel_city_code = task.kwargs.get('citycode')
                        item_hotel_name = content_elem.attrib.get('HotelName')
                        item_hotel_brand_id = content_elem.attrib.get('BrandCode')

                        position_elem = xpath_namespace(content_elem, "HotelInfo//Position")[0]
                        item_hotel_latitude = position_elem.attrib.get('Latitude')
                        item_hotel_longitude = position_elem.attrib.get('Longitude')

                        service_elems = xpath_namespace(content_elem, "HotelInfo/Services/Service")
                        item_hotel_service = ",".join([service.xpath("*[local-name()='DescriptiveText']/text()")[0]
                                            for service in service_elems
                                            if service.attrib["Code"] in HOTEL_SERVICE_CODES])

                        item_room_service = ",".join([service.xpath("*[local-name()='DescriptiveText']/text()")[0]
                                            for service in service_elems
                                            if service.attrib["Code"] in ROOM_SERVICE_CODES])

                        awards_elem = xpath_namespace(content_elem, "AffiliationInfo/Awards")[0]
                        item_hotel_star = awards_elem.xpath("*[local-name()='Award' and @Provider='HotelStarRate']/@Rating")[0]
                        item_hotel_rate = awards_elem.xpath("*[local-name()='Award' and @Provider='CtripStarRate']/@Rating")[0]

                        multimedia_elem = xpath_namespace(content_elem, "MultimediaDescriptions")[0]
                        image_elems = xpath_namespace(multimedia_elem,
                                          "MultimediaDescription/ImageItems/ImageItem")

                        item_image_list = []
                        for image_elem in image_elems:
                            image_url = image_elem.xpath("*[local-name()='ImageFormat']/*[local-name()='URL']/text()")[0]
                            image_type = image_elem.xpath("@Category")[0]
                            image_text = image_elem.xpath("*[local-name()='Description']/@Caption")[0]
                            item_image_dict = {"image_url": image_url,
                                   "image_type": image_type,
                                   "image_text": image_text.encode('utf-8')}
                            item_image_list.append(item_image_dict)

                            if item_hotel_code and image_url:
                                image_item = ImageItem(item_hotel_code, image_type, image_text, image_url)
                                yield image_item

                        text_items_elem = xpath_namespace(multimedia_elem, "MultimediaDescription/TextItems")[0]
                        item_hotel_preview = text_items_elem.xpath(
                            "*[local-name()='TextItem' and @Category='5']/*[local-name()='Description']/text()")[0]

                        room_elems = xpath_namespace(content_elem, "FacilityInfo/GuestRooms/GuestRoom")
                        item_room_list = []
                        for room_elem in room_elems:
                            room_info_id = room_elem.xpath("*[local-name()='TypeRoom']/@RoomTypeCode")[0]
                            room_info_name = room_elem.xpath("@RoomTypeName")[0]
                            room_bed_type = room_elem.xpath("*[local-name()='TypeRoom']/@BedTypeCode")[0]
                            room_net_service, room_net_service_fee = self._extract_net_service(room_elem)
                            room_info_rate_price = ""
                            room_hot = ""
                            room_floor = room_elem.xpath("*[local-name()='TypeRoom']/@Floor")[0]
                            room_breakfast = ""
                            room_area = ""
                            room_info_dict = {'roomInfo_id': room_info_id,
                                      'roomInfo_ratePrice': room_info_rate_price,
                                      'hot': room_hot}
                            item_room_list.append(room_info_dict)

                            room_item = RoomInfoItem(item_hotel_code, room_info_id, room_info_name,
                                            room_floor, room_net_service, room_net_service_fee,
                                            room_bed_type, room_breakfast, room_area)
                            yield room_item

                        hotel_item = HotelInfoItem(item_hotel_code, item_hotel_city_code, item_hotel_name,
                                           item_hotel_brand_id, item_hotel_latitude, item_hotel_longitude,
                                           item_hotel_service, item_room_service, item_hotel_star, item_hotel_rate,
                                           item_image_list, item_hotel_preview, item_room_list)

                        yield hotel_item
                    except Exception, e:
                        self.logger.error("one hotel extract error:%s")
                        print "fuck1"
                        print e
        except Exception, e:
            print e
            raise e
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

