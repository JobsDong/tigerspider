#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from lxml import etree
from StringIO import StringIO
from core.util import xpath_namespace


from spiders.ctrip.util import HOTEL_SERVICE_CODES, ROOM_SERVICE_CODES


def _extract_net_service(room_elem):
    """extract net service

        Args:
            room_elem: _Element
        Returns:
            net_service, service_fee: tuple, (str, str)
    """
    codes = room_elem.xpath("*[local-name()='Amenities']//*[local-name()='Amenity']/@RoomAmenityCode")
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

if __name__ == "__main__":
    with open("/home/wuyadong/Documents/rooms.xml", "rb") as input_file:
        soap_tree = etree.fromstring(input_file.read())
        soap_elems = xpath_namespace(soap_tree,
                            "/soap:Envelope/soap:Body/RequestResponse/RequestResult")
        xml_str = soap_elems[0].text

        tree = etree.fromstring(xml_str)
        elems = tree.xpath("/Response/Header")
        header = elems[0]
        if header.attrib.has_key("ResultCode") and header.attrib['ResultCode'] == "Success":
            content_elem = xpath_namespace(tree,
                                "/Response/HotelResponse/OTA_HotelDescriptiveInfoRS/"
                                "HotelDescriptiveContents/HotelDescriptiveContent")[0]
            item_hotel_code = content_elem.attrib.get('HotelCode')
            item_hotel_city_ctrip = content_elem.attrib.get("HotelCityCode")
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

            text_items_elem = xpath_namespace(multimedia_elem, "MultimediaDescription/TextItems")[0]
            item_hotel_preview = text_items_elem.xpath(
                "*[local-name()='TextItem' and @Category='5']/*[local-name()='Description']/text()")[0]

            room_elems = xpath_namespace(content_elem, "FacilityInfo/GuestRooms/GuestRoom")
            for room_elem in room_elems:
                room_info_id = room_elem.xpath("*[local-name()='TypeRoom']/@RoomTypeCode")[0]
                room_info_name = room_elem.xpath("@RoomTypeName")[0]
                room_bed_type = room_elem.xpath("*[local-name()='TypeRoom']/@BedTypeCode")[0]
                room_net_service, room_net_service_fee = _extract_net_service(room_elem)
                room_info_rate_price = ""
                room_hot = ""
                room_floor = room_elem.xpath("*[local-name()='TypeRoom']/@Floor")[0]
                room_breakfast = ""
                room_area = ""










