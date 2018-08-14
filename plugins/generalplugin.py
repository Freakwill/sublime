# -*- coding: utf-8 -*-

import sublime, sublime_plugin

from . import basic
from . import pyplugin

class FileBasicCommand(basic.BasicCommand):
    indent = '    '
    textcommand = pyplugin.DefFuncCommand

    # self.get_file_type()



class DefFuncCommand(FileBasicCommand):
    def run(self, edit):     
        if self.get_file_type() == '.py':
            self.textcommand.run()
        else:
            pass

class DefClassCommand(FileBasicCommand):
    def run(self, edit):
        pass
