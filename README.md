WegfLaby_AP
===========

Repository zum Robotikpraktikum "Wegfindung im Labyrinth (AP)"

Ordnerstruktur
--------------

* `/steckbrief` für Steckbrief
* `/src` für Quellcode
* `/site` für Webseite
* `/poster` für Poster
* `/presentation` für Präsentation

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
