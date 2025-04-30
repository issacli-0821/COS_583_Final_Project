int multiply(int x, int y) {
    int result = 0;
    while (y > 0) {
        result += x;
        y--;
    }
    return result;
}

// Returns 24
int main() {
    int a = 6;
    int b = 4;
    int product = multiply(a, b);
    return product;
}