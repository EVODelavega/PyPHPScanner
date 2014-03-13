PyPHPScanner
============

Simple way to scan php scripts for use of magic getters/setters. The Scanner.py file can also replace these, statements with an accuracy of approx. 85~90%, so don't trust it blindly...
Use case:

```php
    $instance->protectedProperty = 42;
    echo $instance->protectedProperty;
```

will be replaced with:

```php
    $instance->setProtectedProperty(42);
    echo $instance->getProtectedProperty();
```

Indentation and line-feeds are preserved

## Requirements
 * python3.3 - I've decided to go for the latest stable version of python, not for any particular reason, just because.
 * So far, nothing else. AFAIK, all imports are standard

## Test files

In this repo, you'll find 2 PHP files (test.php and after.php). All I did to create those was write the first (test.php) file, and copy it (`cp test.php after.php`). Then I ran the script, opened the _after.php_ file, and changed the class name `Foo` to `Foo2`, and added the custom getter and setter methods.

This reflects the changes that were made to our framework, and for what it's worth, simply accessing and setting a single property 100 times shows a significant speed difference:

```
Loop took 0.001810ms
Loop took 0.000280ms
Basic example difference is 0.00156
```

These were the results of running the timeDiff.php script. Note that apart from the changes I mentioned (not re-declaring the `Foo` class and _adding_ two methods), the code is unchanged. In reality, we got rid of the magic methods, too. the code, then looks more like the one you see in testOut.php.

## Basic usage:

This is pretty self-explanatory, but still:

```
$ python3.3 Scanner.py -h
```

Should help you out here. Sufficive to say that:

```
$ python3.3 Scanner.py -l1 -d -f > output.tmp
```
will give you a list of what statements or expressions in what files will be changed if you run the same command again, without the `-d` or `--dry` flag.

## History

My main motivation for writing the initial version of this script (Not sure if it still works, even), was that I had to do some rather serious refactoring.
The "core" of our PHP framework had been _"refactored"_ (more like a complete overhaul), and I had to fix several thousand lines of code.

Basically, all of the core objects implemented the magic `__get`, `__set` and `__call` methods, to expose their protected properties. The getter transformed the variable name into a getter, which often did not exist, and in turn invoked the `__call` method, which then translated the getter back into the property name, to finally return a value.
Assigning values to properties worked in a similar fashion, which meant that there was a lot of pointless overhead, endless HashTable lookups going on in the background and what you ended up with was code that was just as error-prone as when you'd write the same classes with nothing but public properties. Only slower.

I decided to give Python a bash (as I'd been putting it off for too long), and wrote a simple script that basically read all .php files, applied a regex to each line, showing me what lines in what files I should fix.
It worked, but still involved quite a lot of manual labour. Since the script was simply a wrapper around 1 regular expression, I decided to turn it into a class, add on some CLI arguments, and work on automatically translating property access to method-calls.

Though far from perfect, I put it up here, so I can work on it some more in my spare time, and in the off chance this script can help someone else who just happens to stumble on it by accident.
Any requests, suggestions, improvements and pull-requests are, of course, welcome.
