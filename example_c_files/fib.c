// Convert to LLVM IR: clang -S -emit-llvm -o fib.ll fib.c

#include <stdio.h>

int main() {
    int n = 10;
    int first = 0;
    int second = 1;
    int fib = 0;

    for (int i = 1; i <= n; i++) {
        fib = first + second;
        first = second;
        second = fib;
    }

    return second;
}
