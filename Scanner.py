#!/usr/bin/env python3.3

import re
import os
import sys
import getopt

  ##################################################
  #      Simple old-school property scanner        #
  #       Interactively scans .php files for       #
  #   ${var}->{property} usage. Skips $this usage  #
  #   and method calls. Lists matches + lines      #
  #          in an attempt to facilitate           #
  #            The refactoring process             #
  #                                                #
  #                 CLI-ARGUMENTS:                 #
  #  --p(ath)=string, specifies the path to scan   #
  #                 defaults to pwd                #
  #  --l(evel)=int specifies the depth of the scan #
  #               Default=0 (no limit)             #
  #  --f(ull) Disables prompting to scan each file #
  #          Default prompt for each file          #
  #  --d(ry) Dry-run the script, it's recommended  #
  #        To redirect output to a tmp file        #
  #       --h simply displays a help message       #
  #                                                #
  #            NOTE: Requires python 3.3           #
  ##################################################

class Scanner:
    extension = '.php'
    pattern = 0
    depth = 0
    path = './'
    dry = False
    full = False
    excludes = []
    accesOfOperator = '->' ## todo?
    
    def __init__ (self, params = {}):
        # optionally pass a dictionary, to set up the class just-so
        setEx = False
        for p, val in params.items():
            if hasattr(self, p) and p != 'excludes':  ## only set existing properties, treat excludes separately
                setattr(self, p, val)
            elif p == 'excludes':
                setEx = True
        if setEx == True: ## onle set after processing the dict, make sure the extension is set
            self.setExcludes(params['excludes'])
    
    #special case for excludes property: check extension, add if required
    def setExcludes(self, exList):
        offset = len(self.extension) * -1
        for ex in exList:
            if ex[offset:] != self.extension:
                ex += self.extension
            print('Added exclude: ', ex)
            self.excludes.append(ex)

    # use setter method, to ensure a string or regex object is assigned to pattern
    def setPattern(self, string):
        if isinstance(re.compile('a'), string):
            self.pattern = string
        else:
            self.pattern = re.compile(string)
        return self
    
    # only use getPattern internally, though slower, it ensures us we have a regex object
    def getPattern(self):
        if self.pattern == 0: ## lazy-load default regex
            self.pattern = re.compile(r'(?<=\$(?!this))(\w+)(?:->)(_?\w+\b)(?!\()')
        elif type(re.compile('a')) != type(self.pattern):
            self.pattern = re.compile(self.pattern)
        return self.pattern

    # pass sys.argv[1:] here, to configure the instance based on CLI arguments
    def parseCliArgs(self, argv):
        try:
            opts, args = getopt.getopt(argv, "hfdl:p:", ["help", "full", "dry", "level=", "path="])
        except getopt.GetoptError as err:
            print(str(err))
            usage()
            sys.exit(2)
        path = self.path
        for o, val in opts:
            if o in ("-h", "--help"):
                usage()
                sys.exit(0)
            elif o in ("-l", "--level"):
                self.depth = int(val)
            elif o in ('-f', '--full'):
                self.full = True
            elif o in ('-d', '--dry'):
                self.dry = True
            elif o in ("-p", "--path"):
                val = val.strip()
                if val[0] == '~':
                    val = val.replace("~", os.getenv('HOME'))
                elif val[0] != '/':
                    path = './'
                if val[-1:] != '/':
                    val += '/'
                path += val
        if len(self.path) == 0:
            self.path = './'
        return self
    
    # recursive method, uses self.path if no Dir is specified
    def scanDir (self, Dir = 0):
        if Dir == 0:
            print('Start scanning from: ', self.path)
            Dir = self.path
        else:
            print('Now scanning: ', Dir)
        todo = []
        files = os.listdir(Dir)
        offset = len(self.extension) * -1
        for i, val in enumerate(files):
            if val[offset:] == self.extension and val not in self.excludes:
                ## do not prompt if full is true (forces everything to true, except for replacing)
                if self.full == True:
                    self.processFile(Dir + val)
                else:
                    k = input(r'Process file "' + Dir + val + '"? [y/N]')
                    if k == 'y':
                        self.processFile(Dir + val) 
            elif os.path.isdir(Dir + val) == True:
                todo.append(Dir + val + '/')
        if self.depth == 1:
            return
        elif self.depth != 0:
            self.depth -= 1
        for i in range(len(todo)):
            if self.full == True:
            ## force recursive scanning withing self.depth range
                self.scanDir(todo[i])
            else:
                k = input('Scan "' + todo[i] + '"?" [Y/n]')
                if k != 'n':
                   self.scanDir(todo[i])
        return self

    def processFile (self, fName):
        p = self.getPattern()
        reqRewrite = False ## avoid re-writing a file that hasn't changed
    ## in case some corrupted or cache files are being read try-catch
        try:
            fp = open(fName)
        ## dry-run shouldn't prompt to re-write lines, it just prints them
            if self.dry == True:
                lnum = 0
                for line in fp:
                    lnum += 1
                    for match in p.finditer(line):
                        print(fName, '@',str(lnum),': Found ', line.strip(), '\n:suggested replacement: ', self.p2GS(line, match).strip())
                fp.close()
                return self
            lines = fp.readlines()
            for lnum, line in enumerate(lines):
                for match in p.finditer(line):
                    repl = input(r'Replace $' + match.group(0) + '@ line ' + str(lnum+1) +'? [y/m/N]')
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
            if reqRewrite == True:
                fp.close()
                fp = open(fName, 'w')
                for line in lines:
                    fp.write(line)
        except UnicodeDecodeError as err:
            print(fName, 'is not a readable file', str(err)) ## this is a non-fatal error, just print msg
        fp.close()
        return self

    # construct replacement string from line + match groups, needs work
    def p2GS(self, line, matches):
        match = matches.group(0)
        offset = line.find(matches.group(0))
        chunks = [line[:offset],matches.group(1)]
        offset += len(matches.group(0))
        ## get or set?
        equal = line[offset:].find('=')
        semicol = line[offset:].find(';')
        # setter
        if (semicol < 0 and equal >= 0) or (equal > 0 and semicol > equal):
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

## help func
def usage():
    print('-h(elp)         : display this message')
    print('-l(evel=)<int>n : Limit recursive search to "n" levels (default 0 = unlimited)')
    print('-p(ath=)<path>  : absolute (or relative to this scrip) path in which to begin search (default pwd)')
    print('-f(ull)         : Perform a full scan, do not prompt to search files individually')
    print('-d(ry)          : dry-run, redirecting the output to a temp file is strongly recommended')

## Process CLI arguments, call functions accordingly
def main (argv):
    scanner = Scanner()
    scanner.parseCliArgs(argv)
    scanner.scanDir()

if __name__ == "__main__":
    main(sys.argv[1:])
