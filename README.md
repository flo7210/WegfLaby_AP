WegfLaby_AP
===========

Repository zum Robotikpraktikum "Wegfindung im Labyrinth (AP)"

Ordnerstruktur
--------------

* `/steckbrief` für Steckbrief
* `/src` für Quellcode
* `/poster` für Poster
* `/praesentation` für Präsentation
* Benutze [Wiki](https://github.com/flo7210/WegfLaby_AP/wiki) für Webseite

Coding style
----------

Für Python:

* Wir folgen [PEP 8](http://legacy.python.org/dev/peps/pep-0008/).
* Insbesondere benutzen wir keine Tabs, sondern Leerzeichen, nämlich 4 Stück.
* Öffentliche Module, Funktionen, Klassen und Methoden sollen einen Docstring beinhalten.
* Kommentare und Namen auf Englisch.

Für TeX:

* Kein `fontspec` package, da nicht kompatibel mit `pdftex`. Stattdessen:
  
  ```tex
  \usepackage[utf8]{inputenc} 
  ```
