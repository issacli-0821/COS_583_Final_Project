int gcd(int first, int second) {
	int temp;

	while (second != 0)
	{
		temp = first % second;
		first = second;
		second = temp;
	}

	return first;
}

int lcm(int first, int second) {
	return (first / gcd(first, second)) * second;
}

int main() {
	int one = 30;
	int two = 20;
	int resultGcd;
	int resultLcm;

	resultGcd = gcd(one, two); // 10
	resultLcm = lcm(one, two); // 60

	return resultGcd * 64 + resultLcm;
}