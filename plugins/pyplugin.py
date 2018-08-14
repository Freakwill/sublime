# -*- coding: utf-8 -*-

import sublime, sublime_plugin

from . import basic

import strparse

class PyBasicCommand(basic.BasicCommand):
    indent = '    '
    message = 'I have completed it. Go on!'

    def send_message(self, msg=None):
        if msg is None:
            msg = self.message
        sublime.status_message(msg)

    def ispyfile(self):
        # filename.endswith('.py')
        return self.get_file_type() == '.py'


class AddQuoteCommand(PyBasicCommand):
    def run(self, edit):
        for sel in self.view.sel():
            b, e = sel.begin(), sel.end()
            if self.get_str(b,3) in ("'''", '"""') and self.get_str(e,-3) in ("'''", '"""'):
                self.view.erase(edit, sublime.Region(e-3, e))
                self.view.erase(edit, sublime.Region(b, b+3))
            else:
                self.view.insert(edit, e, "'''")
                self.view.insert(edit, b, "'''")


class AddMainCommand(PyBasicCommand):
    def run(self, edit):
        r, c = self.get_selected_rowcol()
        if self.iswhiteline(r):
            self.view.replace(edit, self.get_line(r), 'if __name__ == "__main__":')
        else:
            if not self.get_linestr(r).startswith('if __name__ == "__main__":'):
                if self.iswhiteline(r+1):
                    self.view.replace(edit, self.get_line(r+1), 'if __name__ == "__main__":')
                    r += 1
                else:
                    self.view.insert(edit, self.view.text_point(r+1, 0), 'if __name__ == "__main__":\n')
                    r += 1
        for row in range(r+1, len(self)):
            line = self.get_line(row)
            self.view.replace(edit, line, self.indent + self.view.substr(line))


# class FirstLineCommand(PyBasicCommand):
#     firstline = "# -*- coding: utf-8 -*-"

#     def run(self, edit):
#         if self.ispyfile():
#             firstline = self.get_line(0)
#             s = self.view.substr(firstline)
#             ins = self.firstline
#             if s != ins:
#                 if s.startswith('# -'):
#                     self.view.replace(edit, firstline, ins)
#                 else:
#                     if s != '':
#                         ins += '\n'
#                     self.view.insert(edit, 0, ins)


class CleanCommand(PyBasicCommand):
    message = 'I clean the mess.'
    def run(self, edit):
        # clear ; and whitespace at the end of lines
        # clear \n(newline) at the end of the file
        flag = False
        for line in self.lines():
            s0 = self.view.substr(line)
            s = s0.rstrip('; ')
            if s0 != s:
                self.view.replace(edit, line, s)
                if flag is False: flag = True

        for line in self.revert_full_lines():
            s0 = self.view.substr(line)
            if s0 == '\n':
                self.view.erase(edit, line)
                if flag is False: flag = True
            else:
                s = s0.rstrip()
                if s0 != s:
                    self.view.replace(edit, line, s)
                    if flag is False: flag = True
                break
        if flag:
            self.send_message()
        else:
            self.send_message('I did nothing.')


class ParseLineCommand(PyBasicCommand):
    # Base class of command to parse the lines selected
    token = None
    def operate(self, edit, line, pr):
        # override this method if naccessary
        if hasattr(pr, 'code'):
            self.view.replace(edit, line, pr.code())
        else:
            self.view.replace(edit, line, str(pr))

    def run(self, edit):
        for line in self.get_selected_multilines():
            s = self.view.substr(line)
            pr = self.token.parseString(s)[0]  # subclass of Action
            self.operate(edit, line, pr)
        self.send_message()


'''grammar:
import package

MyOwnCommand(ParseLineCommand):
    token = package.parserElement
    def operate(self, edit, line: multi-line, pr: parsing result)
'''

class DefCommand(ParseLineCommand):
    # parse the input
    # generate the codes of definitions of functions, methods and classes
    token = strparse.statement


class CmdCommand(ParseLineCommand):
    token = strparse.command