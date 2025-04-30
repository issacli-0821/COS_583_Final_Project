int main() {
	int n = 1331;
	int reversed = 0;
	int remainder = 0;
	int original = n;

	while (n != 0) {
		remainder = n % 10;
		reversed = reversed * 10 + remainder;
		n /= 10;
	}

	return original == reversed;
}