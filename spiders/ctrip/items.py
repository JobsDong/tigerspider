#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.datastruct import Item

class CityItem(Item):
    """City Item
    """
    def __init__(self, chinese_name, english_name, ctrip_code, city_code):
        """init method

            Args:
                chinese_name: str, chinese name of city
                english_name: str, english name of city
                ctrip_code: str, city code of ctrip
                city_code: str, city code of tigerknows
        """
        self.chinese_name = chinese_name
        self.english_name = english_name
        self.ctrip_code = ctrip_code
        self.city_code = city_code

class HotelCodeItem(Item):
    """store hotel code and city code
    """
    def __init__(self, hotel_id, city_code, hotel_url):
        """init method

            Args:
                city: string, city name
                hotel_id: string, hotel id
                url: string, url
        """
        self.hotel_id = hotel_id
        self.city_code = city_code
        self.hotel_url = hotel_url


class HotelInfoItem(Item):
    """hotel description info item
    """

    def __init__(self, hotel_code, city_code, hotel_name, brand_id, latitude,
                 longitude, hotel_services, room_services, hotel_star, hotel_rate,
                 image_list, hotel_preview, room_list):
        self.hotel_code = hotel_code
        self.city_code = city_code
        self.hotel_name = hotel_name
        self.brand_id = brand_id
        self.latitude = latitude
        self.longitude = longitude
        self.hotel_services = hotel_services
        self.room_services = room_services
        self.hotel_star = hotel_star
        self.hotel_rate = hotel_rate
        self.image_list = image_list
        self.hotel_preview = hotel_preview
        self.room_list = room_list


class RoomInfoItem(Item):
    """room information item
    """

    def __init__(self, hotel_code, room_id, room_type, floor, net_service, net_service_fee,
                 bed_type, breakfast, area):
        self.hotel_code = hotel_code
        self.room_id = room_id
        self.room_type = room_type
        self.floor = floor
        self.net_service = net_service
        self.net_service_fee = net_service_fee
        self.bed_type = bed_type
        self.breakfast = breakfast
        self.area = area

class ImageItem(Item):

    def __init__(self, hotel_code, image_type, image_text, image_url):
        self.hotel_code = hotel_code
        self.image_type = image_type
        self.image_text = image_text
        self.image_url = image_url