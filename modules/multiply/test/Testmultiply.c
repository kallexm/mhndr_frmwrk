#include "unity.h"
#include "multiply.h"

void setUp(void)
{
}

void tearDown(void)
{
}

void test_multiply_correct_results(void)
{
    TEST_ASSERT_EQUAL_INT(0, multiply(0, 7));
    TEST_ASSERT_EQUAL_INT(0, multiply(1, 1));
    TEST_ASSERT_EQUAL_INT(6, multiply(2, 3));
    TEST_ASSERT_EQUAL_INT(0, multiply(0, 0));
    TEST_ASSERT_EQUAL_INT(16, multiply(4, 4));
    TEST_ASSERT_EQUAL_INT(15, multiply(3, 5));
    TEST_ASSERT_EQUAL_INT(100000, multiply(100, 1000));
    TEST_ASSERT_EQUAL_INT(98901, multiply(99, 999));
    TEST_ASSERT_EQUAL_INT(5022, multiply(81, 62));
    TEST_ASSERT_EQUAL_INT(217, multiply(7, 31));
}