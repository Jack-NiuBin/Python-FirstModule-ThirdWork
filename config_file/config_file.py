#!/usr/bin/env python
# -*- coding: utf-8 -*-
#introduction[介绍]  #author:     #time：   #function：   #need

import json
import re
import time
import os

FILE_NAME = "HAproxy.conf"

def parse_file(file_name):
    """
    文件内容解析函数
    :param file_name: 配置文件名称
    :return: list，格式如下：[{node1: [record1, record2, ...},{node2: [record1, record2, ...]},...]
    """
    pattern = "^\s+\w*"
    node_list = []
    with open(file_name, "r") as f:
        start_flag = True
        for line in f:
            if not line.strip():
                continue
            if not re.match(pattern, line):
                node = {}
                node_list.append(node)
                datas = []
                node[line.strip()] = datas
                start_flag = False
            else:
                if start_flag:
                    print("Error happened!")
                    continue
                else:
                    datas.append(line.strip())
    return node_list

def parse_list(haproxy_list):
    """
    写配置文件
    :param haproxy_list: 配置文件信息列表
    :return:
    """
    with open(FILE_NAME, "w") as f:
        for item in haproxy_list:
            for k, v in item.items():
                f.write(k+"\n")
                for s in v:
                    f.write("        "+s+"\n")
            f.write("\n")
    print("操作结果已保存！")


def input_handle(str):
    """
    增删操作时，对输入的记录进行处理
    :param str: 用户输入的配置记录,例{"backend": "test.oldboy.org","record":{"server": "100.1.7.9","weight": 20,"maxconn": 30}}
    :return: 配置项及内容,例{"title":"backend www.oldboy.org", "item":"server 100.1.7.9 100.1.7.9 weight 20 maxconn 3000"}
    """
    input_dict = json.loads(str)
    backend = {}
    try:
        backend["title"] = "backend " + input_dict["backend"]
        backend["item"] = "server %s %s weight %d maxconn %d" % \
                            (input_dict["record"]["server"], input_dict["record"]["server"],
                            input_dict["record"]["weight"], input_dict["record"]["maxconn"])
    except Exception:
        print("输入不合法！")
    return backend

print('''1、获取ha记录
2、增加ha记录
3、删除ha记录
0、退出
''')

while True:
    operation = input("请输入操作序号：").strip()

    if operation.isdigit():
        operation_num = int(operation)
        if operation_num == 0:
            break

        elif operation_num == 1:
            read = input("请输入backend：").strip()
            haproxy_content = parse_file(FILE_NAME)
            backend_title = "backend " + read
            query_empty = True
            for item in haproxy_content:
                if backend_title in item.keys():
                    for s in item[backend_title]:
                        print(s)
                    query_empty = False
            if query_empty:
                print("无相关的输入配置项！")

        elif operation_num == 2:
            read = input("请输入要新增的记录：").strip()
            backend = input_handle(read)
            haproxy_content = parse_file(FILE_NAME)
            add_new = True
            break_flag = False
            backup_flag = False
            # 遍历已有的配置文件，节点存在则增加记录
            for i in range(len(haproxy_content)):
                # 节点存在
                if backend["title"] in haproxy_content[i].keys():

                    server_dict = {}
                    for ss in haproxy_content[i][backend["title"]]:
                        server_dict[ss[:20]] = ss

                    # 记录重复，不操作
                    if backend["item"] in haproxy_content[i][backend["title"]]:
                        print("相同配置信息已存在！")
                        add_new = False
                        break

                    # IP存在，则更新该条记录
                    elif backend["item"][:20] in server_dict.keys():
                        haproxy_content[i][backend["title"]].remove(server_dict[backend["item"][:20]])
                        haproxy_content[i][backend["title"]].append(backend["item"])
                        backup_flag = True
                        add_new = False
                        break

                    # 否则，添加相关记录
                    else:
                        haproxy_content[i][backend["title"]].append(backend["item"])
                        backup_flag = True
                        add_new = False
                        break

            # 节点不存在则新增节点与记录
            if add_new:
                tmp_dict = {}
                tmp_dict[backend["title"]] = [backend["item"], ]
                haproxy_content.append(tmp_dict)
                backup_flag = True

            # 将配置信息更新到文件中
            if backup_flag:
                backup_file_name = FILE_NAME + time.strftime("%Y%m%d%H%M%S")
                os.rename(FILE_NAME, backup_file_name)  # 备份文件
                parse_list(haproxy_content)

        elif operation_num == 3:
            read = input("请输入要删除的记录：").strip()
            backend = input_handle(read)
            haproxy_content = parse_file(FILE_NAME)
            del_flag = False

            # 遍历已有的配置文件，记录存在则删除该条记录
            for i in range(len(haproxy_content)):
                if backend["title"] in haproxy_content[i].keys():
                    for s in haproxy_content[i][backend["title"]]:
                        if s == backend["item"]:
                            haproxy_content[i][backend["title"]].remove(s)

                            # 检查节点若已经为空，则删除节点
                            if not haproxy_content[i][backend["title"]]:
                                haproxy_content.remove(haproxy_content[i])
                            del_flag = True

                            # 将配置信息更新到文件中
                            backup_file_name = FILE_NAME + time.strftime("%Y%m%d%H%M%S")
                            os.rename(FILE_NAME, backup_file_name)  # 备份文件
                            parse_list(haproxy_content)

                            break
                if del_flag:
                    break

            # 记录不存在则打印提示信息
            if not del_flag:
                print("未找到该条记录，删除操作未执行！")

        else:
            print("输入有误，请重新输入！")
            continue
    else:
        print("输入有误，请重新输入！")
        continue