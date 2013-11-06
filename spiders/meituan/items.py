# -*- coding=utf-8 -*-
__author__ = 'wuyadong'

from core.datastruct import Item

class CityItem(Item):
    def __init__(self, chinese_name, city_code):
        self.city_code = city_code
        self.chinese_name = chinese_name

class DealItem(Item):
    def __init__(self, price, city_code, dealid, url, name, discount_type, start_time,
                 end_time, discount, original_price, noticed, pictures, description,
                 deadline, short_desc, content_pic, purchased_number,
                 m_url, appointment, place, save, remaining, limit, refund, contact):

        self.price = price
        self.city_code = city_code
        self.dealid = dealid
        self.url = url
        self.name = name
        self.discount_type = discount_type
        self.start_time = start_time
        self.end_time = end_time
        self.discount = discount
        self.original_price = original_price
        self.noticed = noticed
        self.pictures = pictures
        self.description = description
        self.deadline = deadline
        self.short_desc = short_desc
        self.content_pic = content_pic
        self.purchased_number = purchased_number
        self.m_url = m_url
        self.appointment = appointment
        self.place = place
        self.save = save
        self.remaining = remaining
        self.limit = limit
        self.refund = refund
        self.contact = contact

    def __repr__(self):
        return """{'price':%s, 'city_code':%s, 'dealid':%s, 'url':%s, 'name':%s,
                'discount_type':%s, 'start_time':%s,
                 'end_time':%s, 'discount':%s, 'original_price':%s, 'noticed':%s,
                 'pictures':%s, 'description':%s,
                 'deadline':%s, 'short_desc':%s, 'content_pic':%s, 'purchased_number':%s,
                 'm_url':%s, 'appointment':%s, 'place':%s, 'save':%s, 'remaining':%s,
                 'limit':%s, 'refund':%s, 'contact':%s}""" % (self.price, self.city_code, self.dealid,
                self.url, self.name, self.discount_type, self.start_time, self.end_time, self.discount,
                self.original_price, self.noticed, self.pictures, self.description, self.deadline, self.short_desc,
                self.content_pic, self.purchased_number, self.m_url, self.appointment, self.place, self.save,
                self.remaining, self.limit, self.refund, self.contact)

class WebItem(Item):
    def __init__(self, refund, content_text):
        self.refund = refund
        self.content_text = content_text

    def __repr__(self):
        return "{'refund':%s,'content_text':%s}" % (self.refund, self.content_text)

class PictureItem(Item):
    def __init__(self, picture, path):
        self.picture = picture
        self.path = path