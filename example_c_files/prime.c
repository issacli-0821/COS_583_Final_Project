// Returns 1
int main() {
	int n = 43;
	int flag = 1;

	if (n == 0 || n == 1)
		flag = 0;

	for (int i = 2; i <= n / 2; i++) {
		if (n % i == 0) {
			flag = 0;
			break;
		}
	}

	return flag;
}