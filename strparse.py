# -*- coding: utf-8 -*-
import pyparsing as pp


iden = pp.Word(pp.alphas+'_', pp.alphanums+'_-')
idendot = pp.delimitedList(iden, '.', combine=True)
word = pp.Word(pp.alphanums+'-_:()[]')
lpar = pp.Suppress('(')
rpar = pp.Suppress(')')
defkey = pp.Keyword('def')
clskey = pp.Keyword('class')
selfkey = pp.Keyword('self')
mthkey =  pp.Keyword('mthd') |pp.Keyword('mth') |  pp.Keyword('method')
oprator = pp.oneOf('+ - * / ** ^ & | == != < > <= >= // % << >> ~')
key = defkey | clskey | mthkey
opratorx = pp.oneOf('.* ./')
assign = pp.oneOf('= += -= *= /= **= ^= &= != //= %= <<= >>=')
optrans = {'+':'add','-':'sub','*':'mul','/':'truediv','**':'pow','&':'and','|':'or','^':'xor','<<':'lshift','>>':'rshift','//':'floordiv','%':'mod','==':'eq','<':'lt','>':'gt','<=':'le','>=':'ge'}
fun = iden | oprator
unioptrans={'+':'pos','-':'neg','~':'invert'}

def assigntrans(op):
    return 'i' + optrand[op[:-1]]


# indenx = iden | oprator

class Action:
    """base class for Action"""
    def __init__(self, tokens):
        self.tokens = tokens

    def has(self, s):
        return s in self.tokens

    def __repr__(self):
        return ' '.join(self.tokens)

    def __getitem__(self, key):
        return getattr(self.tokens, key)


class ActionArg(Action):
    def __init__(self, tokens):
        super(ActionArg, self).__init__(tokens)
        self.varname = tokens.varname
        if self.has('value'):
            self.value = tokens.value
        if self.has('type'):
            self.type = tokens.type
        self.replace()

    def replace(self):
        self.varname = self.varname.replace('-','_')
        if self.has('type'):
            self.type = self.type.replace('-','_')
        if self.has('value'):
           self.value = self.value.replace('-','_')

    def doc(self):
        T = self.type if self.has('type') else self.varname.replace('_',' ')
        if self.has('value'):
            return '%s: %s [%s]'%(self.varname, T, self.value)
        else:
            return '%s: %s'%(self.varname, T)

    def __repr__(self):
        if self.has('value'):
            s = '%s=%s'%(self.varname, self.value)
        else:
            s = self.varname
        if self.has('type'):
            s += ':%s'%self.type

    def __eq__(self, other):
        if isinstance(other, str):
            return self.varname == other
        else:
            return self.varname == other.varname

class ActionDef(Action):
    indent_ = '    '
    def __init__(self, tokens):
        super(ActionDef, self).__init__(tokens)
        self.function = optrans.get(tokens.function, tokens.function)
        if self.has('args'):
            self.args = tokens.args
        else:
            self.args =[]
        if self.has('star'):
            self.star = tokens.star
        if self.has('dblstar'):
            self.dblstar = tokens.dblstar
        self.replace()

        if self.has('indent'):
            self.indent = tokens.indent
        else:
            self.indent = ''

        if self.has('star'):
            self.star=tokens.star
        if self.has('dblstar'):
            self.star=tokens.dblstar

    def replace(self):
        for arg in self.args:
            arg.replace()
        self.function = self.function.replace('-','_')

    def argstr(self):
        s = []
        flag = False
        for arg in self.args:
            if arg.has('value'):
                flag = True
                s.append(str(arg))
            else:
                if flag:
                    s.append(str(arg) + '=None')
                else:
                    s.append(str(arg))
        s = ', '.join(s)
        if self.has('star'):
            s += ', ' + self.star
        if self.has('dblstar'):
            s += ', ' + self.dblstar
        return s


    def __repr__(self):
        return '%s(%s)'%(self.function, self.argstr())

    @property
    def arity(self):
        return len(self.args)

    def doc(self):
        d = ''
        if self.arity==1:
            d += '%s has 1 argument\n'%self.function
        elif self.arity>1:
            d += '%s has %d arguments\n'%(self.function, self.arity)
        if self.has('star') or self.has('dblstar'):
            d += self.indent + self.indent_ + 'also has varible arguments\n'
        if self.has('args'):
            d += '\n'.join(self.indent+'    '+arg.doc() for arg in self.args)
        return d

    def code(self):
        return "{indent}def {s}:\n{indent}{indent_}'''{doc}'''\n{indent}{indent_}pass".format(**{'indent':self.indent, 's':self, 'indent_':self.indent_, 'doc':self.doc()})

class ActionMth(ActionDef):
    def __init__(self, tokens):
        super(ActionMth, self).__init__(tokens)
        self.function = '__%s__'%optrans[tokens.function] if tokens.function in optrans else tokens.function


    def __repr__(self):
        if self.argstr()=='':
            return '%s(%s)'%(self.function, 'self')
        else:
            return '%s(%s, %s)'%(self.function, 'self', self.argstr())

    def doc(self):
        d = ''
        if self.arity==1:
            d += '%s has 1 argument (excluding self)\n'%self.function
        elif self.arity>1:
            d += '%s has %d arguments (excluding self)\n'%(self.function, self.arity)
        if self.has('args'):
            d += '\n'.join(self.indent+ self.indent_ +arg.doc() for arg in self.args)
        return d


class ActionOp(ActionMth):
    def __init__(self, tokens):
        super(ActionOp, self).__init__(tokens)
        self.oprator = tokens.function
        if not self.has('oprand1') and (not self.has('oprand2') or tokens.oprand2 == 'self'):
            # op self
            self.args=[]
            self.function = '__%s__'%unioptrans[tokens.function] if tokens.function in optrans else tokens.function
        elif self.has('oprand1'):
            if tokens.oprand1 == 'self': # self op other
                self.args=[tokens.oprand2]
                self.function = '__%s__'%optrans[tokens.function] if tokens.function in optrans else tokens.function
            else: # other op self
                self.args=[tokens.oprand1]
                self.function = '__r%s__'%optrans[tokens.function] if tokens.function in optrans else tokens.function

    def doc(self):
        if self.arity==0:
            d = 'implementation of unary oprator %s\n'%self.oprator
        elif self.arity>0:
            d = 'implementation of binary oprator %s\n'%self.oprator
        return d


class ActionCls(ActionDef):
    def __init__(self, tokens):
        super(ActionCls, self).__init__(tokens)
        self.classname = tokens.classname
        if self.has('supers'):
            self.supers = tokens.supers
        else:
            self.supers = ['object']
        # self.replace()
        self.classname = self.classname.replace('-','_')
        self.supers = [supercls.replace('-','_') for supercls in self.supers]


    def __repr__(self):
        return '%s(%s)'%(self.classname, ', '.join(self.supers))

    def initcode(self):
        s = self.argstr()

        body = ('\n' + self.indent + self.indent_*2).join('self.%s = %s'%(arg.varname, arg.varname) for arg in self.args)
        if self.has('supers'):
            star=[]
            if self.has('star'):
                star.append(self.star)
            if self.has('dblstar'):
                star.append(self.dblstar)
            body = 'super(%s, self).__init__(%s)'%(self.classname, ', '.join(star)) + '\n' + self.indent + self.indent_*2 + body
        return 'def __init__(self, %s):\n%s%s\n'%(s, self.indent + self.indent_*2 ,  body)

    def doc(self):
        d = ''
        if self.arity==1:
            d += '%s has 1 (principal) proptery\n'%self.classname
        elif self.arity>1:
            d += '%s has %d (principal) propteries\n'%(self.classname, self.arity)
        if self.has('args'):
            d += '\n'.join(self.indent + self.indent_ + arg.doc() for arg in self.args)
        return d

    def code(self):
        return "{indent}class {s}:\n{indent}{indent_}'''{doc}'''\n{indent}{indent_}{init}".format(**{'indent':self.indent, 's':self, 'indent_':self.indent_, 'doc':self.doc(), 'init':self.initcode()})


arg = iden('varname') + (pp.Optional(pp.Suppress('=')+word('value')) & pp.Optional(pp.Suppress(':')+word('type')))
arg.setParseAction(ActionArg)

defstatement = pp.Optional(pp.Word(' ')('indent').leaveWhitespace()) + pp.Optional(defkey('keyward')) + fun('function') + pp.Optional(pp.delimitedList(arg, pp.Optional(',').suppress())('args')) + pp.Optional(pp.Combine('*'+iden))('star') + pp.Optional(pp.Combine('**'+iden))('dblstar') +pp.Optional(':')
defstatement.setParseAction(ActionDef)

clsstatement = pp.Optional(pp.Word(' ')('indent').leaveWhitespace()) + clskey.suppress() + iden('classname')  + pp.Optional(pp.Suppress('<')+ pp.delimitedList(idendot))('supers') + pp.Optional(pp.delimitedList(arg, pp.Optional(',').suppress())('args')) + pp.Optional(pp.Combine('*'+iden))('star') + pp.Optional(pp.Combine('**'+iden))('dblstar') +pp.Optional(':')
clsstatement.setParseAction(ActionCls)

mthstatement = pp.Optional(pp.Word(' ')('indent').leaveWhitespace()) + mthkey('keyward') + fun('function') + pp.Optional('self') + pp.Optional(pp.delimitedList(arg, pp.Optional(',').suppress())('args')) + pp.Optional('*args')('star') + pp.Optional('**kwargs')('dblstar') + pp.Optional(':')
mthstatement.setParseAction(ActionMth)

opstatement = mthkey('keyward') + pp.Optional(arg('oprand1')) + oprator('function') + pp.Optional(arg('oprand2'))
opstatement.setParseAction(ActionOp)

statement = opstatement | mthstatement | clsstatement | defstatement


# commands just written in file
class ActionCmd(Action):
    def __init__(self, tokens):
        super(ActionCmd, self).__init__(tokens)
        self.command = tokens.command
        if self.has('args'):
            self.args = tokens.args
        else:
            self.supers = []

    def __repr__(self):
        return '%s(%s)'%(self.command, ', '.join(self.args))

    def code(self):
        return str(self)

command = iden('command') + pp.Optional(pp.delimitedList(pp.Optional('-') + iden, pp.Optional(',').suppress())('args'))
command.setParseAction(ActionCmd)