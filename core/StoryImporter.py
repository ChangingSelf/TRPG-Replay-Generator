#!/usr/bin/env python
# coding: utf-8

# log读取器

import re
import pandas as pd
import numpy as np

class StoryImporter:
    parse_struct = {
        # 2023-06-20 15:50:30 Exception(3247131970)
        # 请不要打扰我的工作啦，我会很困扰的。
        "QQExport" : {
            "new": {
                "cmd"   : "new",
                "regex" : r"^(\d{4}-\d{2}-\d{2} \d{1,2}:\d{1,2}:\d{1,2})\s+(.*?)(\([^)]+\)|\<[^>]+\>)$",
                "ID"    : r"$3",
                "name"  : r"$2",
                "speech": ""
            },
            "add": {
                "cmd"   : "add",
                "regex" : r"^(.+)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
        # 【伊可】Exception 2023/06/20 15:50:30
        # 请不要打扰我的工作啦，我会很困扰的。
        "QQCopy" : {
            "new":{
                "regex" : r"^(【.{0,10}】)?(.+?)\s+(\d{4}/\d{1,2}/\d{1,2}\s+)?(\d{1,2}:\d{1,2}:\d{1,2})$",
                "ID"    : r"$2",
                "name"  : r"$2",
                "speech": ""
            },
            "add": {
                "regex" : r"^(.+)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
        # Exception 2023-06-20 15:50:30
        # 请不要打扰我的工作啦，我会很困扰的。
        "QQChannel" : {
            "new":{
                "regex" : r"^(.+?)\s+(\d{4}-\d{1,2}-\d{1,2})\s+(\d{1,2}:\d{1,2}:\d{1,2})$",
                "ID"    : r"$1",
                "name"  : r"$1",
                "speech": ""
            },
            "add": {
                "regex" : r"^(.+)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
        # [Exception]:请不要打扰我的工作啦，我会很困扰的。
        "RGLoid":{
            "new":{
                "regex" : r"^\[([^\[\]]+?)(,.+?)?\](<.+>)?:(.+?)(<.+>)?({.+})?$",
                "ID"    : r"$1",
                "name"  : r"$1",
                "speech": r"$4"
            }
        },
        # [2023/06/20, 3:50:30 PM] Exception
        # 请不要打扰我的工作啦，我会很困扰的。
        "FVTT":{
            "new":{
                "regex" : r"^\[(\d+\/\d+\/\d+, \d+:\d+:\d+ [AP]M)\] (.+)$",
                "ID"    : r"$2",
                "name"  : r"$2",
                "speech": None
            },
            "add": {
                "regex" : r"^(.+)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
        # 2023/06/20 15:50:30 <Exception>:请不要打扰我的工作啦，我会很困扰的。
        "Rendered":{
            "new":{
                "regex" : r"^(\d{4}\/\d{2}\/\d{2}\s)?(\d{2}:\d{2}:\d{2}\s)?<(.+?)(\([^)]+\))?>:?(.*)$",
                "ID"    : r"$3",
                "name"  : r"$3",
                "speech": r"$5"
            },
            "add": {
                "regex" : r"^(.+)$",
                "ID"    : None,
                "name"  : None,
                "speech": r"$1"
            }
        },
    }
    struct_col = ['ID','name','speech']
    def __init__(self, regex_specify:dict=None) -> None:
        self.log_mode = None
        self.section = {
            "ID"    :"",
            "name"  :"",
            "speech":""
        }
        self.results = pd.DataFrame(columns = self.struct_col)
        self.line_index = 0
        # 如果指定了解析正则结构，则重载类变量
        if regex_specify:
            self.parse_struct = regex_specify
    def load(self,text:str):
        lines = text.split('\n')
        for line in lines:
            if self.log_mode is None:
                self.identify(line=line)
            # 解析，或者pass
            self.parse(line=line)
        # 结束遍历之后，最后记录一次
        self.recode()
    def identify(self,line:str):
        for mode in self.parse_struct:
            regex = self.parse_struct[mode]['new']['regex']
            if re.match(regex,line):
                self.log_mode = mode
                print(self.log_mode)
                return mode
        return None
    def parse(self,line:str):
        if self.log_mode is None:
            return None
        else:
            for cmd in self.parse_struct[self.log_mode]:
                this_cmd = self.parse_struct[self.log_mode][cmd]
                regex = this_cmd['regex']
                M = re.match(regex,line)
                if M:
                    # 执行
                    self.execute(match=M, cmd=cmd, cmd_args=this_cmd)
                    # 跳过循环
                    break
    def execute(self,match:re.Match,cmd:str,cmd_args:dict):
        if cmd == 'add':
            for col in self.struct_col:
                if cmd_args[col]:
                    group_index = int(cmd_args[col][1:])
                    self.section[col] += match.group(group_index) + '\n' # 如果是以多行模式结束，则结尾是换行符！
        elif cmd == 'new':
            self.recode()
            for col in self.struct_col:
                if cmd_args[col]:
                    group_index = int(cmd_args[col][1:])
                    self.section[col] = match.group(group_index)
        else:
            pass
    def recode(self):
        # 始终有一个为空行的0
        # 记录这一行的结果
        self.results.loc[self.line_index] = self.section
        # 清空section
        self.section = {
            "ID"    :"",
            "name"  :"",
            "speech":""
        }
        # 序号+1
        self.line_index += 1
        # 调试
        if self.line_index % 1000 == 0:
            print(self.line_index)
    def get_charactor_ID(self)->list:
        if len(self.results) == 0:
            return []
        else:
            this_result = self.results[1:]
            # 原始ID，是倒序排序的
            raw_ID = this_result['ID'].value_counts()
            # 返回
            return raw_ID.index.to_list()
    def get_charactor_name(self)->pd.Series:
        if len(self.results) == 0:
            return None
        else:
            this_result = self.results.loc[1:]
            names = this_result.groupby('ID')['name'].apply(self.get_possible_valid_name)
            # 检查是否出现了重名
            if names.duplicated().any():
                return names.where(~names.duplicated(), names+'_dup')
            else:
                return names
    def get_possible_valid_name(self,set_of_name:pd.Series):
        # 检索内容中的合法词组
        ID_valid = re.compile('[\w]+')
        name_words = set_of_name.map(ID_valid.findall)
        # 将列表元素的Series展平为一个一一对应Series
        name_words_S = name_words.explode()
        # 统计每个词组出现的频次
        name_words_C = name_words_S.value_counts()
        # 返回出现频次等于最大值的词组成的新词组
        return '_'.join(name_words_C[name_words_C == name_words_C.max()].index)