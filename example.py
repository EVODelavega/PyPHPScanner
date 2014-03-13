from Scanner import Scanner, usage

scanner = Scanner({'depth': 1, 'excludes': ['timeDiff.php', 'after.php', 'testOut.php']})
scanner.scanDir()
