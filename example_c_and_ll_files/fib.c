// Convert to LLVM IR: clang -S -emit-llvm -o fib.ll fib.c

#include <stdio.h>

// %2 = n
// %3 = first
// %4 = second
// %5 = fib
// %6 = i


int main() {
    int n = 30;
    int first = 0;
    int second = 1;
    int fib = 0;

    for (int i = 2; i <= n; i++) {
        fib = first + second;
        first = second;
        second = fib;
    }

    return 0;
}
