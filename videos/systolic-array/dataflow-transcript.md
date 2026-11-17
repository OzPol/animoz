# Dataflow

Now place each output in one processing element. A operands move right. B operands move down. The partial sum stays where it is.

The inputs are staggered at the edges. A matching pair meets at PE[i,j] when step = i + j + k. This creates a diagonal wave of useful work.

Each multiply-and-add is one MAC. A PE without a matching operand pair on this step keeps its current sum.

Only the first PE has matching inputs initially. Its first product enters the local accumulator. Later steps activate more PEs together.

At the final step the 4 accumulators hold the same answers as ordinary matrix multiplication. Passing operands locally did not change the mathematics.

Once a tile finishes, its outputs are captured. The accumulators can then be cleared for the next tile.
