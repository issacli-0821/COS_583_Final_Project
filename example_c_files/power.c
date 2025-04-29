int main()
{
	int base = 3;
	int exp = 4;
	int power = 1;

	for (int i = 0; i < exp; i++)
		power *= base;

	return power;
}
