# Dwarf Fortress Portable Wiki



The official [Dwarf Fortress Wiki](http://dwarffortresswiki.org/) is an
invaluable source of information for playing Dwarf Fortress. Even though DF is
an offline game, playing without the wiki is difficult.

This projects provides a local webserver capable of browsing the DF wiki XML
dump. It contains a crude Wikitext renderer, hacked with some DF Wiki
specific features. When I say “crude”, I mean it. It does not support the whole
Wikitext syntax, and only a small subset of DF Wiki templates.


### Disclaimer

This is a horrible, quick, ugly hack. It works, but it’s far from complete and
will never be. It only supports a small subset of MediaWiki markup and a small
subset of DF Wiki specific templates. Thus some pages will not render
correctly. Nevertheless, most things will be readable and will provide useful
information to the offline player.

## Installation

## Usage Instructions

* Put the file [dump.xml][dump] in the same directory as the python script (df_pwiki.py).
* Run the Python script
* Point your browser at http://localhost:8025

## Screenshots

[![](http://sebsauvage.net/wiki/lib/exe/fetch.php?w=300&tok=dbb512&media=dwarf_fortress:dfpw_1.png)](http://sebsauvage.net/wiki/lib/exe/fetch.php?media=dwarf_fortress:dfpw_1.png)
[![](http://sebsauvage.net/wiki/lib/exe/fetch.php?w=300&tok=864f6a&media=dwarf_fortress:dfpw_2.png)](http://sebsauvage.net/wiki/lib/exe/fetch.php?media=dwarf_fortress:dfpw_2.png)
[![](http://sebsauvage.net/wiki/lib/exe/fetch.php?w=300&tok=fb5799&media=dwarf_fortress:dfpw_3.png)](http://sebsauvage.net/wiki/lib/exe/fetch.php?media=dwarf_fortress:dfpw_3.png)
[![](http://sebsauvage.net/wiki/lib/exe/fetch.php?w=300&tok=923a5c&media=dwarf_fortress:dfpw_4.png)](http://sebsauvage.net/wiki/lib/exe/fetch.php?media=dwarf_fortress:dfpw_4.png)
[![](http://sebsauvage.net/wiki/lib/exe/fetch.php?w=300&tok=f19c6b&media=dwarf_fortress:dfpw_5.png)](http://sebsauvage.net/wiki/lib/exe/fetch.php?media=dwarf_fortress:dfpw_5.png)



## Dependencies

DFPortableWiki is a pure Python 2.7 program. It does not depend on any other lib than Python standard lib.

## License & Credit

DFPortableWiki is licensed under the [zlib/libpng OSI license](http://opensource.org/licenses/Zlib)

Copyright (C) 2012 sebsauvage@sebsauvage.net

[dump]: http://dwarffortresswiki.org/images/dump.xml.bz2
