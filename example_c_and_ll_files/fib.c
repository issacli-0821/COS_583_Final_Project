// Convert to LLVM IR: clang -S -emit-llvm -o fib.ll fib.c

#include <stdio.h>

int main() {
    int n = 30;
    int first = 0, second = 1, fib;

    for (int i = 2; i <= n; i++) {
        fib = first + second;
        first = second;
        second = fib;
    }

    printf("Result: %d\n", second);
    return 0;
}
