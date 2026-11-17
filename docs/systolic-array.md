# Systolic array: animated presentation

This project animates the final Group 2 presentation and its speaker notes.
It preserves the supplied deck's dark palette, native header/footer geometry,
matrix/PE forms, and section titles. CMU Serif follows the shared font setting.
The explanatory diagrams are live Manim objects, not screenshots of slides.

## Watch and render

The [saved presentation](../videos/systolic-array/presentation.mp4) includes the
complete explanation. [Matrices](../videos/systolic-array/matrices.mp4) and
[dataflow](../videos/systolic-array/dataflow.mp4) are reusable individual chapters.
SRT captions, chapter timestamps, and reading transcripts accompany each video.
The [original speaker notes](systolic-array-speaker-notes.md) remain available
alongside the generated explanation.

```bash
animoz render systolic-array presentation --quality medium
animoz render systolic-array matrices
animoz render systolic-array dataflow
animoz render systolic-array all --quality high
```

The complete film builds the matrix rule before putting the outputs inside PEs.
It then follows the data through the hardware, introduces input stalls, explains
tiling, establishes the recorded correctness evidence, and compares compute with
complete-product latency. Transitions retain the current mathematical or hardware
concept rather than replacing it with an unrelated list of boxes.

## What moves, and why

| Concept | Animation |
| --- | --- |
| Matrix multiplication | Highlight one A row and B column, track k, update the partial sum, and retain each completed C entry |
| Output-stationary dataflow | Move matching numbered operands between neighboring PEs while sums stay local |
| Parallelism | Highlight the PEs performing valid MACs on each logical step |
| Scaling | Expand the PE grid and compare P² arithmetic units with 2P peak boundary demand |
| Input staging | Fill a finite word budget, visibly hold a register, and update it only after the full step arrives |
| Tiling | Traverse every output tile in row order, retain captured outputs, and show the full inner dimension |
| Correctness | Show the source experiment's 18 configurations and 144 recorded passing cases |
| Input-supply cost | Separate advance, stall, and capture clocks with values derived from the schedule |
| Readout | Deliver individual result entries through a serial output, then include all N² output clocks |
| Speedup | Compare baseline/candidate clocks for both computation and the complete product |

The small numerical example is a teaching example, not a reconstruction of the
RTL project's random test matrices. With the default settings,

$$
A=\begin{bmatrix}1&2\\3&4\end{bmatrix},\quad
B=\begin{bmatrix}5&6\\7&8\end{bmatrix},\quad
C=\begin{bmatrix}19&22\\43&50\end{bmatrix}.
$$

For A of shape M×K and B of shape K×N,

$$C_{ij}=\sum_{k=0}^{K-1} A_{ik}B_{kj}.$$

At PE(i,j), matching operands meet at logical step s=i+j+k. Logical steps
advance only when the staged boundary input is complete. A physical clock can
therefore pass without a logical advance. The source design uses signed 16-bit
input operands and local 36-bit accumulators.

## Exact schedule and measured evidence

For the square full-tile schedules in the source project, with P dividing N,

$$w_s=2\sum_{i=0}^{P-1}\mathbf{1}[0\le s-i<N].$$

Each logical boundary step consumes

$$q_s=\max\left(1,\left\lceil\frac{w_s}{B}\right\rceil\right)$$

physical clocks. A drain step with no new boundary words still needs one advance.
There are N+2P−2 advances and one capture clock per output tile:

$$T_{compute}=\left(\frac NP\right)^2
\left(1+\sum_{s=0}^{N+2P-3}q_s\right),\qquad
T_{total}=T_{compute}+N^2.$$

This independent model reproduces all 18 source CSV rows exactly for advance,
stall, capture, compute, and total clocks. The default N=16, P=8 schedules are
304, 184, and 124 compute clocks for input budgets 4, 8, and 16. With full supply,
the P=2 baseline uses 1216 compute clocks. Adding 256 serial readout clocks gives
1472 versus 380 total clocks. Compute speedup is 9.81× and complete-product
speedup is 3.87×.

Useful utilization is N³/(P² T_compute), not the fraction of colored boxes in a
diagram. The default full-supply large array has 51.6% useful utilization. Fill,
drain, and capture still consume capacity even when input stalls disappear.

The input budget counts combined A/B operand words per physical clock. It is a
controlled RTL input model, not measured KV260 memory bandwidth. The animation
does not rerun FPGA implementation or claim new hardware measurements.

## Sources and configuration

- `source-slides.json`: native object geometry and original notes extracted from
  `Final_Group2_Systolic_Array_Premium.pptx`, including its source hash.
- `source-simulation.csv`: the source repository's saved complete-product results.
- `sources.json`: pinned repository reference and input hashes.
- `project.toml`: the teaching matrices, pacing, and selected workload/grid/budget.

Source repository: <https://github.com/OzPol/systolic-array-scaling>.

Edit only the appropriate TOML entries or provide a partial `--config` override.
The mathematical model validates compatible rectangular integer matrices. The
displayed example is limited to four rows/columns for readability. Performance
examples use the source experiment's N=8/16, P=2/4/8, and B=4/8/16 settings.
Regenerate both the videos and their metadata after changing the inputs.

```bash
python scripts/verify_renders.py media --project systolic-array --save-to videos/systolic-array
```

`systolic-array` descends from the `puerta-court` commit. Both PRs target main;
the systolic branch contains the Puerta implementation and manual environment
updates as well. Merge Puerta first, then systolic, to review them in order.
