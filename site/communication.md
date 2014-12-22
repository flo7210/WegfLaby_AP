Kommunikation PC - Microcontroller
==================================

Kommunikationsmodell
--------------------
 
Das Protokoll ist asymmetrisch und umfasst zwei Teilnehmer, nämlich den Microcontroller und den PC. Wir nehmen an, dass der Kommunikationskanal frei von Fehlern ist. Der PC übergibt die *Befehle* und der Microcontroller gibt *Antworten*.

Befehle
-------

Ein *Befehl* ist genau sieben Zeichen lang und hat die folgende Syntax:

```
[x-coord],[y-coord]
```

Hier sind `[x-coord]` und `[y-coord]` dreistellige Zahlen zwischen `025` und `555`, die die Koordinaten des Zielpunkts beschreiben, den der Ball erreichen soll.

Antwort
-------

*Antworten* bestehen genau aus einer Zeile. Der Microcontroller wird nur Antworten geben, wenn sich der Ball balanciert hat. Er kann folgende Antworten geben:

* `=0`, wenn der Ball den Zielpunkt noch nicht erreicht hat.
* `=-1`, wenn der Ball den Zielpunkt nicht erreicht hat und (wahrscheinlich) nie erreichen wird.
* `=1`, wenn der Ball den Zielpunkt erreicht hat.

Hier heißt *Zielpunkt erreichen*, wenn sich der Ball in einer festgelegten unmittelbaren Umgebung des Zielpunktes befindet. Die Variable `uint8_t destinationFuzzy`, die die Größe der Umgebung festlegt, liegt in `main.c`. Die Norm, die diese Umgebung beschreibt, wird in der folgenden Funktion in `main.c` angegeben:

```static uint8_t norm(uint8_t x, uint8_t y, uint8_t x2, uint8_t y2)```
