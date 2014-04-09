from re import compile
from os import path, getenv, listdir
from sys import exit
from getopt import GetoptError, getopt


class Scanner:
    extension = '.php'
    pattern = 0
    depth = 0
    path = './'
    scan = False
    dry = False
    full = False
    excludes = []
    accessOfOperator = '->'  # todo?

    def __init__(self, params=None):
        # optionally pass a dictionary, to set up the class just-so
        if not params:
            params = {}
        setEx = False
        for p, val in params.items():
            if hasattr(self, p) and p != 'excludes':  # only set existing properties, treat excludes separately
                setattr(self, p, val)
            elif p == 'excludes':
                setEx = True
        if setEx:  # only set after processing the dict, make sure the extension is set
            self.setExcludes(params['excludes'])

    #special case for excludes property: check extension, add if required
    def setExcludes(self, exList):
        offset = len(self.extension) * -1
        for ex in exList:
            if ex[offset:] != self.extension:
                ex += self.extension
            self.excludes.append(ex)

    # use setter method, to ensure a string or regex object is assigned to pattern
    def setPattern(self, string):
        if isinstance(compile('a'), string):
            self.pattern = string
        else:
            self.pattern = compile(string)
        return self

    # only use _getPattern internally, though slower, it ensures us we have a regex object
    def _getPattern(self):
        if self.pattern == 0:  # lazy-load default regex
            self.pattern = compile(r'(?<=\$(?!this))(\w+)(?:->)(_?\w+\b)(?!\()')
        elif type(compile('a')) != type(self.pattern):
            self.pattern = compile(self.pattern)
        return self.pattern

    # recursive method, uses self.path if no Dir is specified
    def scanDir(self, Dir=0):
        if Dir == 0:
            print('Start scanning from: ', self.path)
            Dir = self.path
        else:
            print('Now scanning: ', Dir)
        if Dir[-1] != '/':
            Dir += '/'
        todo = []
        files = listdir(Dir)
        offset = len(self.extension) * -1
        for i, val in enumerate(files):
            if val[offset:] == self.extension and val not in self.excludes:
                ## do not prompt if full is true (forces everything to true, except for replacing)
                if self.full:
                    self.processFile(Dir + val)
                else:
                    k = input(r'Process file "' + Dir + val + '"? [y/N]')
                    if k == 'y':
                        self.processFile(Dir + val)
            elif path.isdir(Dir + val):
                todo.append(Dir + val + '/')
        if self.depth == 1:
            return
        elif self.depth != 0:
            self.depth -= 1
        for i in range(len(todo)):
            if self.full:
            ## force recursive scanning withing self.depth range
                self.scanDir(todo[i])
            else:
                k = input('Scan "' + todo[i] + '"?" [Y/n]')
                if k != 'n':
                    self.scanDir(todo[i])
        return self

    def processFile(self, fName):
        p = self._getPattern()
        fp = reqRewrite = False  # avoid re-writing a file that hasn't changed
        ## in case some corrupted or cache files are being read try-catch
        try:
            fp = open(fName)
            ## dry-run shouldn't prompt to re-write lines, it just prints them
            if self.dry:
                lnum = 0
                for line in fp:
                    lnum += 1
                    for match in p.finditer(line):
                        print(fName, '@', str(lnum), ': Found ', line.strip())
                        if not self.scan:
                            print('suggested replacement: ', self.p2GS(line, match).strip())
                fp.close()
                return self
            lines = fp.readlines()
            for lnum, line in enumerate(lines):
                for match in p.finditer(line):
                    if self.scan:
                        print(fName, '@', str(lnum), ': Found ', line.strip())
                    else:
                        repl = input(r'Replace $' + match.group(0) + '@ line ' + str(lnum+1) + '? [y/m/N]')
                        repl = repl.lower()
                        if repl == 'y':
                            lines[lnum] = self.p2GS(line, match)
                            reqRewrite = True
                        elif repl == 'm':
                            lines[lnum] = input(r'Please input full replacement line for '+lines[lnum])
                            lines[lnum] += '\n'
                            reqRewrite = True
                        else:
                            print('Not replaced with', self.p2GS(line, match).strip())
            if reqRewrite:
                fp.close()
                fp = open(fName, 'w')
                for line in lines:
                    fp.write(line)
        except UnicodeDecodeError as err:
            print(fName, 'is not a readable file', str(err))  # this is a non-fatal error, just print msg
        if fp:
            fp.close()
        return self

    # construct replacement string from line + match groups, needs work
    def p2GS(self, line, matches):
        offset = line.find(matches.group(0))
        chunks = [line[:offset], matches.group(1)]
        offset += len(matches.group(0))
        ## get or set?
        equal = line[offset:].find('=')
        semicol = line[offset:].find(';')
        # setter
        if (semicol < 0 <= equal) or (0 < equal < semicol):
            chunks.append('->set' + matches.group(2)[0].upper() + matches.group(2)[1:] + '(')
            equal += offset+1
            semicol += offset
            if semicol < 0:
                chunks.append(line[equal:].strip() + ')')
            else:
                chunks.append(line[equal:semicol].strip() + ');\n')
            return ''.join(chunks)
        chunks.append('->get' + matches.group(2)[0].upper() + matches.group(2)[1:] + '()')
        chunks.append(line[offset:])
        return ''.join(chunks)
