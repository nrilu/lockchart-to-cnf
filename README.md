# lockchart-to-cnf

A simple implementation of the SAT encoding of Lock-Charts (Master-Key Systems). Based on Radomír Černochs ["Lock-chart solving"](https://github.com/cernoch/mks-dis/blob/master/LockChartSolvingWeb.pdf) (2017) and Martin Hořeňovskýs [Performance analysis of a
master-key system solver](https://codingnest.com/files/thesis.pdf) (2018).

The script ```lockchart_to_cnf.py``` allows to define lock-charts and to compile them into CNF formulas. It then verifies a solution found by a SAT solver and display the found key and lock designs. 

Submitted to the Benchmark Submissions of the [SAT Competition 2025.](https://satcompetition.github.io/2025/)

# Usage
Run: 

``` ./lockchart_to_cnf.py ```

Optional flags:

```-l ``` Number of locks (default: L=50) \
```-r ``` Probablity for the randomized lock-charts. Per default the lock-charts are structured (default: r=0) \
```-p ``` Number of positions per key (default: P=8) \
```-d ``` Number of depths per key position (default: D=4) 

