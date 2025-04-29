int main() {
	int n = 9183;
	int count = 0;

	do {
		n /= 10;
		count++;
	} while (n != 0);

	return count;
}