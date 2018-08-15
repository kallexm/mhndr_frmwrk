#include "unity.h"
#include "addition.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_addition_correct_results(void)
{
    TEST_ASSERT_EQUAL_INT(7, multiply(0, 7));
    TEST_ASSERT_EQUAL_INT(2, multiply(1, 1));
    TEST_ASSERT_EQUAL_INT(5, multiply(2, 3));
    TEST_ASSERT_EQUAL_INT(0, multiply(0, 0));
    TEST_ASSERT_EQUAL_INT(8, multiply(4, 4));
    TEST_ASSERT_EQUAL_INT(8, multiply(3, 5));
    TEST_ASSERT_EQUAL_INT(1100, multiply(100, 1000));
    TEST_ASSERT_EQUAL_INT(1098, multiply(99, 999));
    TEST_ASSERT_EQUAL_INT(143, multiply(81, 62));
    TEST_ASSERT_EQUAL_INT(38, multiply(7, 31));
}