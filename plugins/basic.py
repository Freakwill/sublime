# -*- coding: utf-8 -*-

import sublime, sublime_plugin

class BasicCommand(sublime_plugin.TextCommand):

    def iseof(self, point=0):
        # end point
        return self.view.substr(point) == chr(0)

    def iseof2(self, row=0):
        # end row
        return self.iseof(self.view.text_point(row, 0))

    def __len__(self):
        # number of rows
        r = 0
        while not self.iseof2(r):
            r += 1
        return r

    def get_line(self, k=0):
        # get line k
        return self.view.line(self.view.text_point(k, 0))

    def get_full_line(self, k=0):
        # get line k
        return self.view.full_line(self.view.text_point(k, 0))
    
    def get_linestr(self, k=0):
        # get the string of line k (exclude /n)
        # int (line number) => string
        return self.view.substr(self.get_line(k))

    def get_selected_lines(self):
        # lines of points selected
        return [self.view.line(point) for point in self.get_selected_points()]

    def get_selected_multilines(self):
        # regions of points selected
        return [self.view.line(sel) for sel in self.view.sel()]

    def get_selected_points(self):
        # end points of selected reigons
        return [sel.end() for sel in self.view.sel()]

    def get_selected_point(self):
        # end of selected regions
        return self.view.sel()[-1].end()

    def get_selected_line(self):
        return self.view.line(self.get_selected_point())

    def get_selected_multiline(self):
        # regions of points selected
        return self.view.line(self.view.sel()[-1])

    def get_selected_rowcol(self):
        # end of selected regions (return row and col)
        return self.view.rowcol(self.get_selected_point())

    def followingLines(self):
        # get lines from current row(included) to last row
        r, c = self.get_selected_rowcol()
        return [self.get_line(k) for k in range(r+1, len(self))]

    def followingRows(self):
        # get lines from current row(included) to last row
        r, c = self.get_selected_rowcol()
        return range(r+1, len(self))

    def leadingLines(self):
        # get lines from 0 to current row(excluded)
        r, c = self.get_selected_rowcol()
        return [self.get_line(k) for k in range(0, r)]

    def iswhiteline(self, row=0):
        import re
        rx = re.compile('\A *\Z')
        if rx.match(self.view.substr(self.get_line(row))):
            return True
        else:
            return False

    def get_file_type(self):
        import os.path
        return os.path.splitext(self.view.file_name())[1]

    def run(self, edit):
        pass

    def get_str(self, start=0, length=1, end=None):
        # get the string of region from start to start+length (or end)
        if length is not None:
            if length >= 0:
                return self.view.substr(sublime.Region(start, start+length))
            else:
                return self.view.substr(sublime.Region(start+length, start))
        elif end is None:
            return self.view.substr(sublime.Region(start, start+1))
        else:
            return self.view.substr(sublime.Region(start, end))

    def get_selected_str(self):
        return [self.view.substr(sel) for sel in self.view.sel()]

    def no_sel(self):
        for sel in self.view.sel():
            if sel.a!=sel.b:
                return False
        return True

    def lines(self):
        for k in range(len(self)):
            yield self.get_line(k)

    def revert_full_lines(self):
        for k in range(len(self)-1, -1, -1):
            yield self.get_full_line(k)


class FirstLineCommand(BasicCommand):
    # firstline = 

    def run(self, edit):
        if self.get_file_type() == '.py':
            firstline = self.get_line(0)
            s = self.view.substr(firstline)
            ins = "# -*- coding: utf-8 -*-"
            if s != ins:
                if s.startswith('# -'):
                    self.view.replace(edit, firstline, ins)
                else:
                    if s != '':
                        ins += '\n'
                    self.view.insert(edit, 0, ins)
        elif self.get_file_type() == '.tex':
            firstline = self.get_line(0)
            s = self.view.substr(firstline)
            ins = "%!TEX program = xelatex"
            if s != ins:
                if s.startswith('%!'):
                    self.view.replace(edit, firstline, ins)
                else:
                    if s != '':
                        ins += '\n'
                    self.view.insert(edit, 0, ins)
