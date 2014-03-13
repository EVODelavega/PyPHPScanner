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
  #  NEW FEATURE => Script now replaces property-  #
  #   access with getter or setter (interactive)   #
  #      this should work on ~85% of the time      #
  #                                                #
  #                 CLI-ARGUMENTS:                 #
  #  --p(ath)=string, specifies the path to scan   #
  #                 defaults to pwd                #
  #  --l(evel)=int specifies the depth of the scan #
  #               Default=0 (no limit)             #
  #  --f(ull) Disables prompting to scan each file #
  #          Default prompt for each file          #
  #       --h simply displays a help message       #
  #                                                #
  #                                                #
  #            NOTE: Requires python 3.3           #
  ##################################################

## Function lists pattern matches + line number
## skips $this->str & method calls
def listProperties (fName, ex = 0):
    p = listProperties.p if ex == 0 else re.compile(ex)
    reqRewrite = False
    fp = open(fName)
    lines = fp.readlines()
    for lnum, line in enumerate(lines):
        for match in p.finditer(line):
            repl = input(r'Replace $' + match.group(0) + '@ line ' + str(lnum+1) +'? [y/m/N]')
            repl = repl.lower()
            if repl == 'y':
                lines[lnum] = p2GS(line, match)
                reqRewrite = True
            elif repl == 'm':
                lines[lnum] = input(r'Please input full replacement line for '+lines[lnum])
                lines[lnum] += '\n'
                reqRewrite = True
            else:
                print('Not replaced with', p2GS(line, match).strip())
    if reqRewrite == True:
        fp.close()
        fp = open(fName, 'w')
        for line in lines:
            fp.write(line)
    fp.close()

## Set function property, have this pattern persist in between calls
## This is, basically, the point of this script
listProperties.p = re.compile(r'(?<=\$(?!this))(\w+)(?:->)(_?\w+\b)(?!\()')

## turn property into getter/setter
def p2GS(line, matches):
    match = matches.group(0)
    offset = line.find(matches.group(0))
    chunks = [line[:offset],matches.group(1)]
    offset += len(matches.group(0))
    ## get or set?
    equal = line[offset:].find('=')
    semicol = line[offset:].find(';')
    if semicol < 0 and equal < 0:
        return line
    # setter?
    if semicol < 0 or (equal > 0 and semicol > equal):
        chunks.append('->set' + matches.group(2)[0].upper() + matches.group(2)[1:] + '(')
        equal += offset+1
        semicol += offset
        if semicol < 0:
            chunks.append(line[equal:].strip() + ')')
        else:
            chunks.append(line[equal:semicol].strip() + ');\n')
        return ''.join(chunks)
    chunks.append('->get' + matches.group(2)[0].upper() + matches.group(2)[1:] + '()')
    semicol += offset
    chunks.append(line[semicol:])
    return ''.join(chunks)

## iterates through directories
def processDir (depth, Dir = './', full = False):
    todo = []
    print('Scanning: ' + Dir)
    files = os.listdir(Dir)
    for i, val in enumerate(files):
        if val[-4:] == '.php':
            if full == True:
                k = 'y'
            else:
                k = input(r'Process file "' + Dir + val + '"? [y/N]')
            if k == 'y':
                listProperties(Dir + val) 
        else:
            if os.path.isdir(Dir + val) == True:
                todo.append(Dir + val + '/')
    if depth == 1:
        return
    elif depth != 0:
        depth -= 1
    for i in range(len(todo)):
        k = input('Scan "' + todo[i] + '"?" [Y/n]')
        if k != 'n':
            processDir(depth, todo[i])
## help func
def usage():
    print('-h(elp)         : display this message')
    print('-l(evel=)<int>n : Limit recursive search to "n" levels (default 0 = unlimited)')
    print('-p(ath=)<path>  : absolute (or relative to this scrip) path in which to begin search (default pwd)')
    print('-f(ull)         : Perform a full scan, do not prompt to search files individually')
    print('-d(ry)          : dry-run, redirecting the output to a temp file is strongly recommended')

## Process CLI arguments, call functions accordingly
def main (argv):
    depth = 0
    path = ''
    full = False
    try:
        opts, args = getopt.getopt(argv, "hfdl:p:", ["help", "full", "dry", "level=", "path="])
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)
    for o, val in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        elif o in ("-l", "--level"):
            depth = int(val)
        elif o in ('-f', '--full'):
            full = True
        elif o in ("-p", "--path"):
            val = val.strip()
            if val[0] == '~':
                val = val.replace("~", os.getenv('HOME'))
            elif val[0] != '/':
                path = './'
            if val[-1:] != '/':
                val += '/'
            path += val
    if len(path) == 0:
        path = './'
    print ('Scanning ', path, ' ', depth, ' levels deep')
    processDir(depth, path, full)

if __name__ == "__main__":
	main(sys.argv[1:])
