======================================
ctrip
======================================

功能
=======

用于携程酒店信息的数据抓取

抓取源
=============

调用ctrip的酒店查询api,通过API获取数据

有关数据库
==============

最终抓取的数据是放在线上的swift数据库的rthotel_ctrip_hotel,
rthotel_ctrip_image, rthotel_ctrip_roomlist, rthotel_ctrip_urllist表中

建rthotel_ctrip_hotel表的sql如下::

  -- Table: rthotel_ctrip_hotel

  -- DROP TABLE rthotel_ctrip_hotel;

  CREATE TABLE rthotel_ctrip_hotel
  (
    id serial NOT NULL,
    city_code character varying NOT NULL,
    hotel_id character varying NOT NULL,
    url character varying NOT NULL,
    info character varying NOT NULL,
    add_time timestamp without time zone,
    CONSTRAINT unique_url_citycode_hotel_id UNIQUE (url , city_code , hotel_id )
  )
  WITH (
    OIDS=FALSE
  );
  ALTER TABLE rthotel_ctrip_hotel
    OWNER TO postgres;

  -- Index: rthotel_ctrip_hotel_add_time_btree

  -- DROP INDEX rthotel_ctrip_hotel_add_time_btree;

  CREATE INDEX rthotel_ctrip_hotel_add_time_btree
    ON rthotel_ctrip_hotel
    USING btree
    (add_time );

  -- Index: rthotel_ctrip_hotel_url_btree

  -- DROP INDEX rthotel_ctrip_hotel_url_btree;

  CREATE INDEX rthotel_ctrip_hotel_url_btree
    ON rthotel_ctrip_hotel
    USING btree
    (url );

建rthotel_ctrip_image表的sql如下::

  -- Table: rthotel_ctrip_image

  -- DROP TABLE rthotel_ctrip_image;

  CREATE TABLE rthotel_ctrip_image
  (
    id bigserial NOT NULL,
    siteid text,
    image_type text,
    image_text text,
    image_url text,
    ischeck boolean NOT NULL DEFAULT false,
    addtime timestamp without time zone,
    CONSTRAINT rthotel_ctrip_image_pkey PRIMARY KEY (id ),
    CONSTRAINT uq_ctrip_omage_url UNIQUE (image_url )
  )
  WITH (
    OIDS=FALSE
  );
  ALTER TABLE rthotel_ctrip_image
    OWNER TO postgres;

  -- Index: rthotel_ctrip_siteid

  -- DROP INDEX rthotel_ctrip_siteid;

  CREATE INDEX rthotel_ctrip_siteid
    ON rthotel_ctrip_image
    USING hash
    (siteid );


建rthotel_ctrip_roomlist表的sql语句::

  -- Table: rthotel_ctrip_roomlist

  -- DROP TABLE rthotel_ctrip_roomlist;

  CREATE TABLE rthotel_ctrip_roomlist
  (
    id bigserial NOT NULL,
    cityname character varying(50),
    hotel_id character varying(20),
    room_id character varying(20),
    ischeck boolean NOT NULL DEFAULT false,
    statuscode integer,
    roominfo text,
    rateinfo text,
    checktime timestamp without time zone,
    addtime timestamp without time zone,
    CONSTRAINT rthotel_ctrip_roomlist_pkey PRIMARY KEY (id ),
    CONSTRAINT "unique rthotel_ctrip_roomlist_cityname_hotelid_roomid_unique" UNIQUE (cityname , hotel_id , room_id )
  )
  WITH (
    OIDS=FALSE
  );
  ALTER TABLE rthotel_ctrip_roomlist
    OWNER TO postgres;

  -- Index: rthotel_ctrip_roomlist_cityname_hotelid_roomid_index

  -- DROP INDEX rthotel_ctrip_roomlist_cityname_hotelid_roomid_index;

  CREATE INDEX rthotel_ctrip_roomlist_cityname_hotelid_roomid_index
    ON rthotel_ctrip_roomlist
    USING btree
    (cityname , hotel_id , room_id );


建rthotel_ctrip_urllist表的sql语句::

  -- Table: rthotel_ctrip_urllist

  -- DROP TABLE rthotel_ctrip_urllist;

  CREATE TABLE rthotel_ctrip_urllist
  (
    id bigserial NOT NULL,
    cityname text,
    shopurl text,
    isright boolean,
    ischeck boolean NOT NULL DEFAULT false,
    statuscode integer,
    extendinfo text,
    checktime timestamp without time zone,
    addtime timestamp without time zone,
    CONSTRAINT rthotel_ctrip_urllist_pkey PRIMARY KEY (id ),
    CONSTRAINT "unique rthotel_ctrip_urllist_shopurl" UNIQUE (shopurl )
  )
  WITH (
    OIDS=FALSE
  );
  ALTER TABLE rthotel_ctrip_urllist
    OWNER TO postgres;

  -- Index: rthotel_ctrip_cityname

  -- DROP INDEX rthotel_ctrip_cityname;

  CREATE INDEX rthotel_ctrip_cityname
    ON rthotel_ctrip_urllist
    USING hash
    (cityname );

  -- Index: rthotel_ctrip_shopurl

  -- DROP INDEX rthotel_ctrip_shopurl;

  CREATE INDEX rthotel_ctrip_shopurl
    ON rthotel_ctrip_urllist
    USING hash
    (shopurl );


部署和运行
===============

部署运行
-----------

* 获得代码 git clone git@github.com:JobsDong/tigerspider.git

* 修改配置:

  * 修改监控端口

    1235就是默认端口号

    修改 ``tigerknows-spider/monitor.py`` ::

      if __name__ == "__main__"
          walk_settings()
          web_service = WebService()
          web_service.start(1235)
  * 修改数据保存的数据库地址

    127.0.0.1就是数据库的ip, 5432就是数据库的端口, postgres是数据库的用户名
    titps4gg是数据库的密码，是数据库的名字
    修改 ``tigerknows-spider/spiders/ctrip/pipeline.py`` ::

        class HotelCodeItemPipeline(BasePipeline):

            def __init__(self, namespace, db_host="127.0.0.1", db_port=5432,
                         db_user="postgres", db_password="titps4gg", db_base="swift"):

        class RoomInfoItemPipeline(BasePipeline):
            def __init__(self, namespace, db_host="127.0.0.1", db_port=5432,
                         db_user="postgres", db_password="titps4gg", db_base="swift"):

        class HotelInfoItemPipeline(BasePipeline):
            def __init__(self, namespace, db_host="127.0.0.1", db_port=5432,
                         db_user="postgres", db_password="titps4gg", db_base="swift"):

        class ImageItemPipeline(BasePipeline):
            def __init__(self, namespace, db_host="127.0.0.1", db_port=5432, db_user="postgres",
                         db_password="titps4gg", db_base="swift"):


  * 运行monitor.py 程序::

      python monitory.py &

  * 通过api启动任务

    在浏览器中输入: ``http://{host}:{port}/api/start_worker?schedule_path=schedules.schedules.RedisSchedule&spider_path=spiders.ctrip.spider.DianPingImageUrlSpider&schedule_interval=400&schedule_max_number=20``

    * host是对应的部署的机器的ip
    * port是对应的监控端口
    * schedule_path是要使用的schedule_path，能够使用的schedule请参看tigerknows-spider/settings/registersettings
    * spider_path是使用的spider_path,能够使用的spider请参看tigerknows-spider/settings/registersettings
    * schedule_interval是每次请求的抓取间隔，单位是ms
    * schedule_max_number是请求的最大并发度

  * iceage的定时任务配置::

    #ctrip
    10 09 * * 1 curl "http://127.0.0.1:1238/api/start_worker?schedule_path=schedules.canrepeatschedule.RepeatRedisSchedule&spider_path=spiders.ctrip.spider.CtripSpider&schedule_interval=2000&schedule_max_number=5"

