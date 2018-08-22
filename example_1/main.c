#include <stdio.h>

#include "addition.h"

int main()
{
    int one = 1;
    int two = 2;

    int sum = add(one, two);

    printf("sum %i", sum);
    return 0;
}