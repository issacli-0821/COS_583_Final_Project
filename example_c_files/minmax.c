int max(int first, int second, int third)
{
	int max;
	if (first >= second) {
		max = first;
	}
	else {
		max = second;
	}
	
	if (third > max) {
		max = third;
	}
	
	return max;
}

int min(int first, int second, int third)
{
	int min;
	if (first <= second) {
		min = first;
	}
	else {
		min = second;
	}
	
	if (third < min) {
		min = third;
	}
	
	return min;
}

int mean(int first, int second, int third)
{
	return (first + second + third) / 3;
}

int main()
{
	int one = 2;
	int two = 7;
	int three = 3;
	int maxInt;
	int minInt;
	int meanInt;
	
	maxInt = max(one, two, three);
	minInt = min(one, two, three);
	meanInt = mean(one, two, three);
	
	return maxInt * 64 + minInt * 8 + meanInt;
}