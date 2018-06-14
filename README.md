Ping check a list of hosts
==========================

*take a list of space or comma seperated hosts and ping check them.*
*accept also slurm node range expression*

This script was tested using python3 3.6.3

Usage
-----
```
./WhoIsUp.py nodeA[1,3,5,12,22,24-27,29-30,33,37-40],nodeB[1,3-6,9],nodeC[1-3],nodeD1 nodeE1,NodeE2 nodeF1, nodeF2
```
```
./WhoIsUp.py nodeA{1..33} nodeA{34..36}, nodeA[37-39] nodeA40, nodeA41,nodeA42
```


