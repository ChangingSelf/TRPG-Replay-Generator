#!/usr/bin/env python
# coding: utf-8

import ttkbootstrap as ttk
from .GUI_Util import KeyValueDescribe, TextSeparator
from .GUI_EditTableStruct import TableStruct
from .ScriptParser import MediaDef
# 编辑区

# 编辑窗
class EditWindow(ttk.LabelFrame):
    TableStruct = TableStruct
    def __init__(self,master,screenzoom):
        # 初始化基类
        self.sz = screenzoom
        super().__init__(master=master,bootstyle='primary',text='编辑区')
        self.page = master
        # 初始化状态
        self.line_type = 'no_selection'
        self.elements = {}
        self.seperator = {}
        self.section:dict = None
        # 更新
        self.update_item()
    def update_item(self):
        SZ_5 = int(5*self.sz)
        SZ_15 = int(15*self.sz)
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.pack(side='top',anchor='n',fill='x',pady=(0,SZ_5),padx=(SZ_5,SZ_15))
    def clear_item(self):
        for key in self.elements:
            item:KeyValueDescribe = self.elements[key]
            item.destroy()
        for key in self.seperator:
            item:TextSeparator = self.seperator[key]
            item.destroy()
        self.elements.clear()
        self.seperator.clear()
    # 从小节中更新窗体内容
    def update_from_section(self,index:str,section:dict,line_type):
        # 清除
        self.clear_item()
        self.section = section
        # 确定页类型
        self.table_struct:dict = self.TableStruct[line_type]
        # 编辑区
        for sep in self.table_struct:
            this_sep:dict = self.table_struct[sep]
            self.seperator[sep] = TextSeparator(
                master=self,
                screenzoom=self.sz,
                describe=this_sep['Text']
            )
            for key in this_sep['Content']:
                this_kvd:dict = this_sep['Content'][key]
                # 如果valuekey判断valuekey
                if this_kvd['valuekey'] == '$key':
                    this_value = index
                elif this_kvd['valuekey'] in self.section.keys():
                    this_value = self.struct_2_value(self.section[this_kvd['valuekey']])
                else:
                    this_value = this_kvd['default']
                self.elements[key] = self.seperator[sep].add_element(key=key, value=this_value, kvd=this_kvd)
    # 从section的值转为显示的value
    def struct_2_value(self,section):
        return section
    def value_2_struct(self,value):
        return value
    # 将窗体内容覆盖到小节
    def write_section(self):
        self.section.clear()
    # 获取可用立绘、气泡名
    def get_avaliable_anime(self)->list:
        return self.page.ref_medef.get_type('anime')
    def get_avaliable_bubble(self)->list:
        return self.page.ref_medef.get_type('bubble')
    def get_avaliable_text(self)->list:
        return self.page.ref_medef.get_type('text')
    def get_avaliable_pos(self)->list:
        return self.page.ref_medef.get_type('pos')
class CharactorEdit(EditWindow):
    custom_col = []
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = TableStruct['CharTable']
    def update_from_section(self,index:str,section:dict,line_type='charactor'):
        super().update_from_section(index,section,line_type=line_type)
        # 媒体
        self.elements['Animation'].input.configure(values=['NA']+self.get_avaliable_anime(),state='readonly')
        self.elements['Bubble'].input.configure(values=['NA']+self.get_avaliable_bubble(),state='readonly')
        # 音源
        for ele in ['Voice','SpeechRate','PitchRate']:
            self.elements[ele].describe.configure(command=lambda :self.open_voice_selection(
                master=self,
                voice=self.elements['Voice'].get(),
                speech_rate=self.elements['SpeechRate'].get(),
                pitch_rate=self.elements['PitchRate'].get(),
            ))
        # 更新
        self.update_item()
    # 打开音源选择窗
    def open_voice_selection(self, master, voice, speech_rate, pitch_rate):
        print(voice,speech_rate,pitch_rate)
class MediaEdit(EditWindow):
    medef_tool = MediaDef()
    def __init__(self, master, screenzoom):
        super().__init__(master, screenzoom)
        self.TableStruct = TableStruct['MediaDef']
    def update_from_section(self,index:str,section: dict, line_type):
        super().update_from_section(index, section, line_type)
        # TODO:各个类型的config
        # 更新
        self.update_item()
    def struct_2_value(self,section):
        return self.medef_tool.value_export(section)