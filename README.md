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

## History

My main motivation for writing the initial version of this script (Not sure if it still works, even), was that I had to do some rather serious refactoring.
The "core" of our PHP framework had been _"refactored"_ (more like a complete overhaul), and I had to fix several thousand lines of code.

Basically, all of the core objects implemented the magic `__get`, `__set` and `__call` methods, to expose their protected properties. The getter transformed the variable name into a getter, which often did not exist, and in turn invoked the `__call` method, which then translated the getter back into the property name, to finally return a value.
Assigning values to properties worked in a similar fashion, which meant that there was a lot of pointless overhead, endless HashTable lookups going on in the background and what you ended up with was code that was just as error-prone as when you'd write the same classes with nothing but public properties. Only slower.

I decided to give Python a bash (as I'd been putting it off for too long), and wrote a simple script that basically read all .php files, applied a regex to each line, showing me what lines in what files I should fix.
It worked, but still involved quite a lot of manual labour. Since the script was simply a wrapper around 1 regular expression, I decided to turn it into a class, add on some CLI arguments, and work on automatically translating property access to method-calls.

Though far from perfect, I put it up here, so I can work on it some more in my spare time, and in the off chance this script can help someone else who just happens to stumble on it by accident.
Any requests, suggestions, improvements and pull-requests are, of course, welcome.
