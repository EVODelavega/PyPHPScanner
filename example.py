from Scanner import Scanner, usage

scanner = Scanner({'depth': 1, 'excludes': ['timeDiff.php', 'after.php', 'testOut.php']})
scanner.scanDir()
myScanner = Scanner({'extension': '.log', 'pattern': r'^err', 'depth': 1, 'path': '/var/log', 'scan':True, 'full': True})
myScanner.scanDir()
