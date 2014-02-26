#!/usr/bin/python
#-*- coding=utf-8 -*-

__author__ = ['"wuyadong" <wuyadong@tigerknows.com>']


import csv


def write_proxys(proxys, dat_path):
    """将proxys写入dat_path文件中
        Args:
            proxys: set, [(host, port)]
            dat_path: str, dat文件路径
    """
    with open(dat_path, "wb") as out_file:
        csv_writer = csv.writer(out_file, lineterminator="\n")
        for host, port in proxys:
            csv_writer.writerow([host.encode('utf-8'), port])


def read_proxys(dat_path):
    """将proxy读入
        Args:
            dat_path: str, dat文件路径
        Returns:
            proxy_set: set, proxy集合
    """
    proxy_set = set()
    with open(dat_path, "rb") as in_file:
        csv_reader = csv.reader(in_file, lineterminator="\n")
        for line in csv_reader:
            host, port = line[0], line[1]
            proxy_set.add((str(host), int(port)))
    return proxy_set