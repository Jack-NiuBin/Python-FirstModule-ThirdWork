#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author:Jack Niu

# 导入使用模块
import os

# 定义打印操作列表函数:
def PrintDomain():
    """
    打印四个选项，分别为查询记录，添加记录，删除记录，更新记录。
    :return:
    """
    from prettytable import PrettyTable

    UserChoice = PrettyTable( ["ID", "Opertation"] )
    UserChoice.align["ID"] = 1
    UserChoice.padding_width = 1
    UserChoice.add_row( [1, "\033[31;1m 查询记录 \033[0m"] )
    UserChoice.add_row( [2, "\033[31;1m 添加记录 \033[0m"] )
    UserChoice.add_row( [3, "\033[31;1m 删除记录 \033[0m"] )
    UserChoice.add_row( [4, "\033[31;1m 更新记录 \033[0m"] )
    print( "########\033[34;1m 欢迎使用Haproxy文件脚本，你可以使用以下操作方式\033[0m########" )
    print( UserChoice )

# 定义判断备份函数:
def BackupFile():
    """
    判断备份文件是否存在，存在则删除后重新备份，不存在则直接备份，此处不使用文件名加时间方式备份。
    :return:
    """
    CopyFlag = os.path.exists( "Haproxy,bak" )
    if CopyFlag == False:
        os.system( "cp Haproxy Haproxy.bak" )
    else:
        os.remove( "Haproxy.bak" )
        os.system( "cp Haproxy Haproxy.bak" )

# 定义输入函数：
def User_Input():
    """
    根据用户输入转化字典。
    :return:
    """
    AddDomainInput = input( "请输入需要操作的内容>>>>>>:" ).strip( )
    AddDomainInput = AddDomainInput.replace( "arg =", "" ).strip( )
    AddDomainInput = AddDomainInput.replace( "\"\"\"", "" ).strip( )
    AddInputDic = eval( AddDomainInput )
    ServerIP = AddInputDic["record"]["server"]
    Weight = AddInputDic["record"]["weight"]
    Maxconn = AddInputDic["record"]["maxconn"]
    RepLine = "        server %s %s weight %s maxconn %s\n" % (ServerIP, ServerIP, Weight, Maxconn)
    return AddInputDic, ServerIP, Weight, Maxconn, RepLine

# 定义全局变量标志位：
SearchFlag = False
WriteFlag = False
SearchNoneFlag = False
RepeatFlag = False

# 定义查询函数:
def SearchDomain(SearchFlag, SearchNoneFlag):
    """
    此函数为查询函数，主要作用为用户输入域名后，根据域名查询对应的行，并且设置标志位，将对应的行和下面的行加入列表，直到发现backend,
    如果没有发现则返回查询域名记录不存在。
    :param:
    :return:
    """
    SearchDomainInput = input( "请输入需要查询的域名>>>>>>:" ).strip( )
    ResultList = []
    with open( "Haproxy", "r" ) as OpenFile:
        for SearchLine in OpenFile:
            if SearchLine.startswith( "backend" ) and SearchDomainInput in SearchLine:
                SearchFlag = True
                SearchNoneFlag = True
                continue
            if SearchLine.strip( ).startswith( "backend" ):
                SearchFlag = False
            if SearchFlag:
                print( SearchLine.strip( ) )
    if SearchNoneFlag == False:
        print( "对不起，你要查询的域名记录\033[32;1m%s\033[0m不存在！" % SearchDomainInput )

# 定义添加函数:
def AddDomain(SearchFlag, WriteFlag, RepeatFlag):
    """
    此函数为添加函数，用户输入后，查询是否有记录，有则在原记录后添加，无则在最后添加.
    :param SearchFlag, WriteFlag, ServerIP, RepLine:
    :return:
    """
    UserRerun = User_Input()
    AddInputDic = UserRerun[0]
    ServerIP = UserRerun[1]
    Weight = UserRerun[2]
    Maxconn = UserRerun[3]
    RepLine = UserRerun[4]
    BackupFile( )
    ResultList = []
    with open( "Haproxy", 'r' ) as OpenFile:
        for Line in OpenFile:
            if Line.startswith( "backend" ) and AddInputDic["backend"] in Line:
                SearchFlag = True
                continue
            if Line.strip( ).startswith( "backend" ):
                SearchFlag = False
            if SearchFlag:
                ResultList.append(Line.strip())
    for ListLine in ResultList:
        if ServerIP in ListLine:
            RepeatFlag = True
    with open( "Haproxy", 'r' ) as OpenFile, open( "HaproxyBackFile", "w+" ) as BackFile:
        for Line in OpenFile:
            if Line.startswith( "backend" ) and AddInputDic["backend"] in Line:
                SearchFlag = True
                WriteFlag = True
                BackFile.write( Line )
                continue
            if Line.strip( ).startswith( "backend" ):
                SearchFlag = False
            if SearchFlag:
                if Line.strip() == RepLine.strip():
                    print("该域名记录已存在")
                    BackFile.write(Line)
                    continue
                elif ServerIP in Line:
                    Line = Line.replace(Line, RepLine)
                if RepeatFlag == False:
                    BackFile.write(RepLine)
                    print( "你好，你需要添加的域名记录\033[32;1m%s\033[0m已经添加成功" % AddInputDic["backend"] )
                    SearchFlag = False
            BackFile.write( Line )
        if WriteFlag == False:
            BackFile.write( "\nbackend %s \n" % AddInputDic["backend"] )
            BackFile.write(RepLine)
            print("你好，你需要添加的域名记录\033[32;1m%s\033[0m已经添加成功" %AddInputDic["backend"])

        os.remove("Haproxy")
        os.rename("HaproxyBackFile", "Haproxy")

# 定义更新域名记录函数：
def UpdateDomain(SearchFlag, WriteFlag):
    """
    若域名相同则退出并不更新，若不相同则进行修改。
    :param SearchFlag, WriteFlag, ServerIP, RepLine:
    :return:
    """
    UserRerun = User_Input()
    AddInputDic = UserRerun[0]
    ServerIP = UserRerun[1]
    Weight = UserRerun[2]
    Maxconn = UserRerun[3]
    RepLine = UserRerun[4]
    BackupFile( )
    with open( "Haproxy", 'r' ) as OpenFile, open( "HaproxyBackFile", "w+" ) as BackFile:
        for Line in OpenFile:
            if Line.startswith( "backend" ) and AddInputDic["backend"] in Line:
                SearchFlag = True
                BackFile.write( Line )
                continue
            if Line.strip( ).startswith( "backend" ):
                SearchFlag = False
            if SearchFlag:
                if ServerIP in Line:
                    Line = Line.replace(Line, RepLine)
                    WriteFlag = True
            BackFile.write( Line )
        if WriteFlag == True:
            print("您的域名记录更新成功！")
        elif WriteFlag == False:
            print("您需要更新的域名记录不存在！")
        os.remove("Haproxy")
        os.rename("HaproxyBackFile", "Haproxy")

# 定义删除函数：
def DeleteDomain(SearchFlag, WriteFlag):
    """
    先将能够删除的记录加入列表，判断需要删除的记录是否位于列表中，如果不存在，则直接退出，如果存在，判断是否只有一条，如果只有一条，
    则删除backend和记录，如果多于一条，则保留backend和域名，只删除记录。
    :param SearchFlag, WriteFlag, ServerIP, RepLine:
    :return:
    """
    UserRerun = User_Input()
    AddInputDic = UserRerun[0]
    ServerIP = UserRerun[1]
    Weight = UserRerun[2]
    Maxconn = UserRerun[3]
    RepLine = UserRerun[4]
    BackupFile( )
    ResultList = []
    with open( "Haproxy", 'r' ) as OpenFile:
        for Line in OpenFile:
            if Line.startswith( "backend" ) and AddInputDic["backend"] in Line:
                SearchFlag = True
                continue
            if Line.strip( ).startswith( "backend" ):
                SearchFlag = False
            if SearchFlag:
                ResultList.append(Line.strip())
    with open( "Haproxy", 'r' ) as OpenFile, open( "HaproxyBackFile", "w+" ) as BackFile:
        for Line in OpenFile:
            if not ResultList:
                print("您要删除的域名记录不存在！")
                WriteFlag = True
                os.remove("HaproxyBackFile")
                break
            if RepLine.strip() in ResultList:
                if len(ResultList) == 2:
                    if AddInputDic["backend"] in Line or ServerIP in Line.strip():
                        continue
                if len(ResultList) > 2:
                    if ServerIP in Line.strip():
                        continue
            if RepLine.strip() not in ResultList:
                print("您要删除的域名记录不存在！")
                WriteFlag = True
                os.remove("HaproxyBackFile")
                break
            BackFile.write(Line)
    if WriteFlag == False:
        os.remove("Haproxy")
        os.rename("HaproxyBackFile", "Haproxy")
        print("您的域名记录删除成功！")

# 根据用户选择调用不通的函数：
def User_Choice():
    """
    根据用户的输入，调用不同的函数来执行。
    :return:
    """
    UserInputChoice = input( "请输入您要操作文件的方式，请选择ID操作>>>>>>:" ).strip( )
    if UserInputChoice.isdigit:
        UserInputChoice = int( UserInputChoice )
        if UserInputChoice == 1:
            SearchDomain(SearchFlag, SearchNoneFlag)
        elif UserInputChoice == 2:
            AddDomain(SearchFlag, WriteFlag, RepeatFlag)
        elif UserInputChoice == 3:
            DeleteDomain(SearchFlag, WriteFlag)
        elif UserInputChoice == 4:
            UpdateDomain( SearchFlag, WriteFlag)

# 定义主要流程函数：
def main():
    """
    主函数，作用为打印列表和输入。
    :return:
    """
    PrintDomain()
    User_Choice()

# 运行主函数
if __name__ == '__main__':
    main()
