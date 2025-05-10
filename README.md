# lockchart-to-cnf

A simple implementation of compiling Lock-Charts (Master-Key Systems) into SAT CNF formulas. Heavily based on Radomír Černochs ["Lock-chart solving"](https://github.com/cernoch/mks-dis/blob/master/LockChartSolvingWeb.pdf) (2017) and Martin Hořeňovskýs [Performance analysis of a
master-key system solver](https://codingnest.com/files/thesis.pdf) (2018).

Define a lock-chart and geometric key-constraints, compile it into a CNF formula.

Submitted to the Benchmark Submissions of the [SAT Competition 2025.](https://satcompetition.github.io/2025/)

# Usage
Run: 

``` ./lockchart_to_cnf.py ```

Optional flags:

```-l ``` Number of locks (default: L=50) \
```-r ``` Probablity for the randomized lock-charts. Per default the lock-charts are structured (default: r=0) \
```-p ``` Number of positions per key (default: P=8) \
```-d ``` Number of depths per key position (default: D=4) 

