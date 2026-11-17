# Presentation

A systolic array is a team of small arithmetic units. We will follow the numbers first, then see why adding units does not guarantee proportional speedup.

Our source project compares 2 by 2, 4 by 4, and 8 by 8 grids. Each must complete the same matrix product.

A processing element, or PE, repeatedly multiplies two numbers and adds the product to its local running sum. We can understand the entire machine from that one operation.

A matrix is a table of numbers. Multiplication pairs one row of A with one column of B to produce one entry of C.

A's columns must match B's rows. Here the shared length is 2, so each output sum contains 2 products.

The index k walks through the matching entries. The summation sign means that we add every matched product.

The running sum is 0. Multiply 1 by 5, then add that product. The new sum is 5.

The running sum is 5. Multiply 2 by 7, then add that product. The new sum is 19.

That completes one output entry. It stays in C while the same row-column rule fills the other positions.

The completed matrix contains every row-column dot product. The arithmetic rule is simple; the architectural challenge is delivering each matching pair at the right time.

Now place each output in one processing element. A operands move right. B operands move down. The partial sum stays where it is.

The inputs are staggered at the edges. A matching pair meets at PE[i,j] when step = i + j + k. This creates a diagonal wave of useful work.

Each multiply-and-add is one MAC. A PE without a matching operand pair on this step keeps its current sum.

Only the first PE has matching inputs initially. Its first product enters the local accumulator. Later steps activate more PEs together.

At the final step the 4 accumulators hold the same answers as ordinary matrix multiplication. Passing operands locally did not change the mathematics.

Once a tile finishes, its outputs are captured. The accumulators can then be cleared for the next tile.

A P by P grid contains P squared processing elements. Doubling P gives four times as many arithmetic units.

For P equal to 4, that is 16 PEs. But a fully supplied boundary step may also need 8 combined A and B words.

For P equal to 8, that is 64 PEs. But a fully supplied boundary step may also need 16 combined A and B words.

Compute capacity grows with area, P squared. Peak boundary demand grows with edge length, 2P. We must compare both with the available input budget.

Consider one full boundary step for a 8 by 8 grid. It needs 16 combined operand words. Our configured interface supplies at most 8 words per physical clock.

Physical clock 1: 8 of 16 words are now staged. The grid still holds all its registers.

Physical clock 2: 16 of 16 words are now staged. The complete step is ready, so the grid can advance.

A clock is a hardware tick. The example register stayed at 5 while waiting. Only the completed input step allowed 5 plus 2 times 7 to become 19.

This example uses a full interior boundary step. Actual demand is smaller during fill and drain, so the complete cycle model counts every step separately.

The complete system must supply operands, perform arithmetic, and deliver results. Improving only the arithmetic leaves the other costs in the path.

We will separate these costs: input stalls, the finite matrix schedule, tile capture, and serial readout. That makes the performance comparison explainable.

A 2 by 2 grid stores one output tile at a time. A complete 8 by 8 product requires 16 such tiles.

The tiles proceed across each row. Green entries have been captured and stay stored while the processing elements move on.

Each tile still streams the full inner dimension. Capture its results, clear the accumulators, then start the next output tile.

A 4 by 4 grid stores one output tile at a time. A complete 8 by 8 product requires 4 such tiles.

A 8 by 8 grid stores one output tile at a time. A complete 8 by 8 product requires 1 such tiles.

Tiling lets smaller hardware compute the same full answer. It changes scheduling and overhead; it does not discard matrix entries.

The source RTL project records 18 configurations, with eight numerical cases each: 144 passing cases. The reported results come from the saved source experiment.

Our animation model independently checks the matrix outputs and reproduces every recorded cycle schedule. It does not rerun Vivado or claim new FPGA measurements.

The word budget is a controlled RTL input model. It is not a measurement of physical KV260 memory bandwidth.

Keep the same 8 by 8 grid and the same 16 by 16 product. The useful arithmetic does not change; only the input word budget changes.

The computed schedules are 304, 184, and 124 clocks. The blue stall segment shrinks as more operands arrive per clock.

From the smallest to largest input budget, latency falls by 59 percent. The mint advance work and gold capture work remain unchanged.

Computation finishing does not mean the whole answer has left the accelerator. The source design reads one output element per clock.

A complete 16 by 16 output has 256 elements. Serial delivery adds exactly 256 clocks after compute. The counter now fast-forwards through the remaining outputs.

At full supply, 124 compute clocks become 380 clocks for the complete product. The same 256-clock readout cost is included in the smaller-grid baseline.

Speedup means baseline clocks divided by candidate clocks. Including readout changes the result substantially, even though the arithmetic hardware is identical.

Larger grids were fastest in the recorded sweep, but extra PEs did not produce proportional speedup. Operand supply, finite scheduling, and result delivery each limited the gain.

A smaller grid can be a deliberate choice when DSP resources matter more than minimum latency. The right answer depends on the complete workload and system constraints.

The matrix rule never changed. What changed was how quickly the system could feed, execute, and finish that rule.
