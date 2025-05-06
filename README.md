# lockchart-to-cnf

An implementation of Radomír Černoch's ["Lock-chart solving"](https://github.com/cernoch/mks-dis/blob/master/LockChartSolvingWeb.pdf) SAT encoding, submitted to the SAT 2025 Competition Benchmark Submissions.

Allows to define simple lock-charts and to compile them into CNF formulas. 

Verifies and displays the key and lock geometries found by a SAT solver solution. 

# Usage
Run: 

``` ./lockchart_to_cnf.py ```

Optional flags:

```-l ``` Number of locks (default: L=50) \
```-r ``` Probablity for the randomized lock-charts. Per default the lock-charts are structured (default: r=0) \
```-p ``` Number of positions per key (default: P=8) \
```-d ``` Number of depths per key position (default: D=4) 

