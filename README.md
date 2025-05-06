# lockchart-to-cnf

An implementation of the SAT encoding of Lock-Chart Master-Key Systems, following Radomír Černoch's ["Lock-chart solving"](https://github.com/cernoch/mks-dis/blob/master/LockChartSolvingWeb.pdf) (2017).  
It allows to define simple lock-charts and to compile them into CNF formulas. 

Verifies the solutions found by a SAT solver and displays the explicit key and lock geometries. Submitted to the Benchmark Submissions of the [SAT Competition 2025.](https://satcompetition.github.io/2025/)

# Usage
Run: 

``` ./lockchart_to_cnf.py ```

Optional flags:

```-l ``` Number of locks (default: L=50) \
```-r ``` Probablity for the randomized lock-charts. Per default the lock-charts are structured (default: r=0) \
```-p ``` Number of positions per key (default: P=8) \
```-d ``` Number of depths per key position (default: D=4) 

