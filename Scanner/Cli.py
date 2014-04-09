import Scanner
from os import getenv
from sys import argv
from getopt import getopt, GetoptError


class Cli(Scanner):
    def __init__(self, args = None):
        if not args:
            args = argv[1:]
        self.parseCliArgs(args)

    # pass sys.argv[1:] here, to configure the instance based on CLI arguments
    def parseCliArgs(self, argv):
        try:
            opts, args = getopt(argv, "hfsdl:p:", ["help", "full", "scan", "dry", "level=", "path="])
        except GetoptError as err:
            print(str(err))
            usage()
            exit(2)
        path = self.path
        for o, val in opts:
            if o in ("-h", "--help"):
                usage()
                exit(0)
            elif o in ("-l", "--level"):
                self.depth = int(val)
            elif o in ('-f', '--full'):
                self.full = True
            elif o in ('-s', '--scan'):
                self.scan = True
            elif o in ('-d', '--dry'):
                self.dry = True
            elif o in ("-p", "--path"):
                val = val.strip()
                if val[0] == '~':
                    val = val.replace("~", getenv('HOME'))
                elif val[0] != '/':
                    path = './'
                if val[-1:] != '/':
                    val += '/'
                path += val
        if len(self.path) == 0:
            self.path = './'
        return self


## help func
def usage():
    print('-h(elp)         : display this message')
    print('-l(evel=)<int>n : Limit recursive search to "n" levels (default 0 = unlimited)')
    print('-p(ath=)<path>  : absolute (or relative to this scrip) path in which to begin search (default pwd)')
    print('-f(ull)         : Perform a full scan, do not prompt to search files individually')
    print('-d(ry)          : dry-run, redirecting the output to a temp file is strongly recommended')
    print('-s(can)         : Scan only, just match pattern, without suggesting/trying to refactor/replace')
