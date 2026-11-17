# Matrices

A matrix is a table of numbers. Multiplication pairs one row of A with one column of B to produce one entry of C.

A's columns must match B's rows. Here the shared length is 2, so each output sum contains 2 products.

The index k walks through the matching entries. The summation sign means that we add every matched product.

The running sum is 0. Multiply 1 by 5, then add that product. The new sum is 5.

The running sum is 5. Multiply 2 by 7, then add that product. The new sum is 19.

That completes one output entry. It stays in C while the same row-column rule fills the other positions.

The completed matrix contains every row-column dot product. The arithmetic rule is simple; the architectural challenge is delivering each matching pair at the right time.
