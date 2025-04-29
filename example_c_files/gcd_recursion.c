int gcd(int one, int two) {
	if (two != 0) {
		return gcd(two, one % two);
	}	
	else {
		return one;
	}
}

int main() {
	int one = 512;
	int two = 257;
	return gcd(one, two);
}