#!/usr/bin/python2.7
#-*- coding=utf-8 -*-

# Copy Rights (c) Beijing TigerKnows Technology Co., Ltd.

__authors__ = ['"wuyadong" <wuyadong@tigerknows.com>']

from core.redistools import RedisPriorityQueue


proxys = [
    {'proxy': 'proxy1', 'priority': 1},
    {'proxy': 'proxy2', 'priority': 1},
    {'proxy': 'proxy3', 'priority': 2},
    {'proxy': 'proxy4', 'priority': 2},
    {'proxy': 'proxy5', 'priority': 3},
    {'proxy': 'proxy6', 'priority': 3},
    {'proxy': 'proxy7', 'priority': 3},
    {'proxy': 'proxy8', 'priority': 4},
    {'proxy': 'proxy9', 'priority': 5},
    {'proxy': 'proxy10', 'priority': 6},
]

def priority_statistic_change(score, m=5):
    return score - m

# def priority_dynamic_change(dynamic, score, m=10, gab=30):
#     return dynamic - m * (float(score) / gab)

def priority_dynamic_change(dynamic, score, m=10, gab=30):
    return dynamic - gab/ score

if __name__ == "__main__":
    que = RedisPriorityQueue("proxy-test", host='localhost', port=6379,)
    for proxy in proxys:
        que.push(proxy, proxy['priority'])


    # 不进行时间调整
    # for i in xrange(0, 20):
    #     proxy, score = que.pop()
    #     print proxy, score
    #     que.push(proxy, score)
    #     if i == 9:
    #         print "fuck"


    #进行时间调整 (调整未len)
    # min_count = max_count = 0
    # for i in xrange(0, 500):
    #     proxy, score = que.pop()
    #     print proxy['proxy']
    #     if proxy['proxy'] == 'proxy10': max_count += 1
    #     if proxy['proxy'] == 'proxy1': min_count += 1
    #     que.push(proxy, priority_change(score))
    #     if i == 9:
    #         print "fuck"
    # print "max:", max_count, "min:", min_count


    # 进行时间调整 （调整为len/2）
    # min_count = max_count = 0
    # for i in xrange(0, 500):
    #     proxy, score = que.pop()
    #     if proxy['proxy'] == 'proxy10': max_count += 1
    #     if proxy['proxy'] == 'proxy1': min_count += 1
    #     que.push(proxy, priority_change(score, 5))
    #     if i == 9:
    #         print "fuck"
    # print "max:", max_count, "min:", min_count

    # 进行时间调整 （调整为len/2）
    # min_count = max_count = 0
    # for i in xrange(0, 500):
    #     proxy, score = que.pop()
    #     if proxy['proxy'] == 'proxy10': max_count += 1
    #     if proxy['proxy'] == 'proxy1': min_count += 1
    #     que.push(proxy, priority_statistic_change(score, 5))
    #     if i == 9:
    #         print "fuck"
    # print "max:", max_count, "min:", min_count

    # # 进行时间调整 (动态调整)
    # min_count = max_count = min2_count = 0
    # for i in xrange(0, 300):
    #     proxy, score = que.pop()
    #     if proxy['proxy'] == 'proxy2': max_count += 1
    #     if proxy['proxy'] == 'proxy1': min_count += 1
    #     if proxy['proxy'] == 'proxy10': min2_count += 1
    #     dynamic = priority_dynamic_change(score, proxy.get('priority'))
    #     print proxy, dynamic
    #     que.push(proxy, dynamic)
    #     if i == 9:
    #         print "fuck"
    # print "max:", max_count, "min:", min_count, "min2:", min2_count

    # 进行反馈调整
    # min_count = max_count = min2_count = 0
    # for i in xrange(0, 300):
    #     proxy, score = que.pop()
    #     if proxy['proxy'] == 'proxy2': max_count += 1
    #     if proxy['proxy'] == 'proxy1': min_count += 1
    #     if proxy['proxy'] == 'proxy10': min2_count += 1
    #     dynamic = priority_dynamic_change(score, proxy.get('priority'))
    #     print proxy, dynamic
    #     que.push(proxy, dynamic)
    #     if i == 9:
    #         print "fuck"
    # print "max:", max_count, "min:", min_count, "min2:", min2_count
    #
    #from core.util import gcd
    #print gcd(1,3), gcd(2,4), gcd(5, 15, 25)
    from core.proxy import ProxyManager
    proxy = ProxyManager.instance().get_an_avaliable_proxy()
    print proxy.host, proxy.port, proxy.score