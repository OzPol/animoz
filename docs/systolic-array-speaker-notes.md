# Original speaker notes

Source: Final_Group2_Systolic_Array_Premium.pptx

These are the source notes, with slide-number placeholders omitted. The animation supplies a separate timed explanation.

## Slide 1

Hello, we're Group 2: Thomas Martin, Ozlem Polat, and Keith Kamer. Today, we'll be presenting our EEL5764 project on systolic array scaling under modeled input bandwidth limits.

## Slide 2

The question we set out to answer is whether a bigger processing-element grid actually delivers proportional speedup once input supply and output overhead are considered.
We compare two-by-two, four-by-four, and eight-by-eight arrays on the same matrix workloads and under controlled input limits. That lets us separate the benefit of extra arithmetic from the cost of keeping that hardware busy.

## Slide 3

First, what is a systolic array? 
A systolic array is a grid of small processing elements, or PEs, that work together to perform calculations.
In our design, values from matrix A move horizontally through the grid, while values from matrix B move vertically.
Each processing element multiplies its incoming values and adds the result to a local accumulator.
This allows many calculations to happen in parallel, which makes systolic arrays particularly useful for matrix multiplication and AI accelerators.

## Slide 4

The mathematics behind each processing element is fairly straightforward.
For matrix multiplication, each output is calculated by multiplying corresponding elements from a row of A and a column of B, then summing those products.
In this example, we start with zero. One times five gives us five, and then we add two times seven, giving us nineteen.
Each processing element performs this multiply-and-accumulate operation repeatedly to produce its assigned output.

## Slide 5

The problem we're investigating is that increasing the number of processing elements doesn't necessarily result in proportional performance improvements.
A two-by-two array has four processing elements, while an eight-by-eight array has sixty-four.
That gives us sixteen times the theoretical compute capacity.
However, the larger array also requires more input data to keep those elements working. Without sufficient input supply, some of that additional processing capability goes unused.

## Slide 6

Here's a concrete example of that bottleneck.
Our eight-by-eight array can require up to sixteen combined input words for a full processing step.
If the input interface supplies only eight words per clock, it takes two clocks to collect those operands.
During that time, the array must hold its current state until the complete step is available.
This introduces stalls, reducing the performance benefit of having more processing elements.

## Slide 7

This is important because accelerator performance depends on more than arithmetic capacity.
We also need to consider how quickly operands arrive and how much time is spent filling the pipeline, processing matrix tiles, and reading completed results.
Adding more hardware increases resource costs, so the real architectural question is whether the additional performance justifies those resources.

## Slide 8

To investigate this, we developed a parameterized, output-stationary systolic array in VHDL.
We compared three grid sizes: two-by-two, four-by-four, and eight-by-eight.
Each grid performs complete eight-by-eight and sixteen-by-sixteen matrix multiplications, with input budgets of four, eight, or sixteen words per clock.
Smaller grids divide the output into tiles to perform the same overall computation.
This gives us a controlled comparison where the architecture, workload size, and input supply can be evaluated systematically.

## Slide 9

Our experimental setup produced eighteen configurations, and we tested each one using eight numerical cases.
That gave us 144 correctness tests, all of which passed.
We verified the outputs using an independent Python reference and ran our simulations in both Questa and GHDL.
After establishing correctness, we measured computation cycles, stalls, and utilization, and used Vivado to evaluate FPGA resource usage and timing.

## Slide 10

Our first major finding demonstrates the effect of input supply.
Using the eight-by-eight array to multiply two sixteen-by-sixteen matrices, we measured 304 compute cycles with a four-word input budget.
Increasing the budget to eight words reduced this to 184 cycles, and sixteen words reduced it further to 124 cycles.
That's approximately a 59 percent reduction in latency without changing the processing-element grid.
The difference comes from reducing input staging delays and stalls.

## Slide 11

Our second finding concerns hardware scaling efficiency.
With full input supply, the eight-by-eight array achieved a 9.81-times compute speedup compared with the two-by-two baseline.
However, it required sixteen times as many processing elements and DSP blocks.
Furthermore, when we included the time required to read out the complete matrix, the speedup dropped to just 3.87 times.

## Slide 12

Our results show that larger systolic arrays can provide substantial performance improvements, but the gains aren't proportional to the additional hardware.
Input bandwidth, pipeline overhead, tiling, and result delivery all influence the final performance.
For our tested configurations, the eight-by-eight grid was consistently the fastest, but the smaller grids offered different tradeoffs in hardware efficiency.
Ultimately, accelerator design is about balancing computation with the rest of the system, rather than simply maximizing the number of processing elements.
Thank you.
