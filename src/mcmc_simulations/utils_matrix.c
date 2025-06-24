/*
Copyright (c) 2025 fastei team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include "utils_matrix.h"
#include <math.h>
#ifdef _OPENMP
#include <omp.h> // Parallelization
#endif
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#ifndef BLAS_INT
#define BLAS_INT int
#endif
// ----------------------------------------------------------------------------
// Utility functions
// ----------------------------------------------------------------------------

/**
 * @brief Checks if the matrix is well defined
 *
 * Given a pointer to a matrix, it verifies if the matrix is well alocated and defined and throws an error if there's
 * something wrong.
 *
 * @param[in] m A pointer to the matrix
 *
 * @return void
 *
 * @note
 * - This will just throw errors, note that EXIT_FAILURE will dealocate memory
 *
 * @warning
 * - The pointer may be NULL.
 * - The dimensions may be negative.
 */
void makeArray(double *array, int N, double value)
{
    if (!array)
    {
    }

    if (N < 0)
    {
    }

    // Fill the array with the specified constant value
    for (int i = 0; i < N; i++)
    {
        array[i] = value;
    }
}

void checkMatrix(const Matrix *m)
{

    // Validation, checks NULL pointer
    if (!m || !m->data)
    {
    }

    // Checks dimensions
    if (m->rows <= 0 || m->cols <= 0)
    {
    }
}

/**
 * @brief Creates an empty dynamically allocated memory matrix of given dimensions.
 *
 * Given certain dimensions of rows and colums, creates an empty Matrix with allocated memory towards the data.
 *
 * @param[in] rows The number of rows of the new matrix.
 * @param[in] cols The number of columns of the new matrix.
 *
 * @return Matrix Empty matrix of dimensions (rows x cols) with allocated memory for its data.
 *
 * @note
 * - Remember to free the memory! It can be made with freeMatrix() call
 *
 * @warning
 * - The memory may be full.
 * - If dimensions are negative.
 */

Matrix createMatrix(int rows, int cols)
{
    if (rows <= 0 || cols <= 0)
    {
    }

    Matrix m;
    m.rows = rows;
    m.cols = cols;

    m.data = calloc(rows * cols, sizeof(double));

    if (!m.data)
    {
    }

    return m;
}

/**
 * @brief Liberates the allocated matrix data.
 *
 * @param[in] m The matrix to free the data.
 *
 * @return void Changes to be made on the input matrix and memory.
 *
 */

void freeMatrix(Matrix *m)
{
    // TODO: Implement a validation warning.
    if (m != NULL && m->data != NULL)
    {
        free(m->data);
        m->data = NULL;
    }
    m->rows = 0;
    m->cols = 0;
}

/**
 * @brief Prints the matrix data.
 *
 * @param[in] m The matrix to print the data.
 *
 * @return void No return, prints a message on the console.
 *
 * @note
 * - Use the function mainly for debugging.
 */

void printMatrix(const Matrix *matrix)
{
    checkMatrix(matrix); // Assertion

    printf("Matrix (%dx%d):\n", matrix->rows, matrix->cols);

    for (int i = 0; i < matrix->rows; i++)
    {
        printf("| ");
        for (int j = 0; j < matrix->cols - 1; j++)
        {
            printf("%.3f\t", MATRIX_AT_PTR(matrix, i, j));
        }
        printf("%.3f", MATRIX_AT_PTR(matrix, i, matrix->cols - 1));
        printf(" |\n");
    }
}

/**
 * @brief Computes a row-wise sum.
 *
 * Given a matrix, it computes the sum over all the rows and stores them in an array.
 * @param[in] matrix Pointer to the input matrix.
 * @param[out] result Pointer of the resulting array of length `rows`.
 *
 * @return void Written on *result
 *
 * @note
 * - Matrix should be in col-major order
 * - This function uses cBLAS library, where the operation can be written as a matrix product
 *   of X * 1.
 * - Just support double type
 *
 * @example
 * Example usage:
 * @code
 *
 * double data[6] = {
 *     1.0, 2.0, 3.0,
 *     4.0, 5.0, 6.0
 * };
 *
 * Matrix matrix = {
 * .data = values,
 * .rows = 2,
 * .cols = 3
 * }
 *
 * double result[matrix->rows]
 *
 * rowSum(matrix, result);
 * // result now contains [6.0, 15.0]
 * @endcode
 */

/**
 * @brief Fills matrix with a constant value.
 *
 * Given a matrix, it fills a whole matrix with a constant value.
 *
 * @param[in, out] matrix Pointer to matrix to be filled.
 * @param[in] value The constant value to fill
 *
 * @return void Written on the input matrix
 *
 * @note
 * - Matrix should be in col-major order.
 *
 * @example
 * Example usage:
 * @code
 * double values[6] = {
 *     1.0, 2.0, 3.0,
 *     4.0, 5.0, 6.0
 * };
 * Matrix matrix = {
 * .data = values,
 * .rows = 2,
 * .cols = 3
 * }
 *
 * fillMatrix(matrix, 9);
 * // matrix->data now contains [9.0, 9.0, 9.0, ..., 9.0]
 * @endcode
 */

void fillMatrix(Matrix *matrix, const double value)
{
    checkMatrix(matrix); // Assertion
    int size = matrix->rows * matrix->cols;

    makeArray(matrix->data, size, value);
}
Matrix copMatrix(const Matrix *original)
{
    checkMatrix(original); // Ensure the original matrix is valid

    // Create a new matrix with the same dimensions
    Matrix copy = createMatrix(original->rows, original->cols);

    // Copy the data from the original matrix
    for (int i = 0; i < original->rows; i++)
    {
        for (int j = 0; j < original->cols; j++)
        {
            MATRIX_AT(copy, i, j) = MATRIX_AT_PTR(original, i, j);
        }
    }

    return copy;
}
/**
 * @brief Creates a copy of the given Matrix.
 *
 * @param orig Pointer to the original Matrix.
 * @return Pointer to a new Matrix that is a copy of orig.
 *
 * This function uses malloc to allocate memory for both the Matrix struct and its data array.
 * The caller is responsible for freeing the memory (using free) when it is no longer needed.
 */
Matrix *copMatrixPtr(const Matrix *orig)
{
    // Allocate memory for the new Matrix structure.
    Matrix *copy = (Matrix *)calloc(1, sizeof(Matrix));
    if (copy == NULL)
    {
    }

    // Copy the dimensions.
    copy->rows = orig->rows;
    copy->cols = orig->cols;

    // Compute the total number of elements.
    int totalElements = orig->rows * orig->cols;

    // Allocate memory for the data array.
    copy->data = (double *)calloc(totalElements, sizeof(double));
    if (copy->data == NULL)
    {
        free(copy);
    }

    // Copy the data from the original matrix.
    memcpy(copy->data, orig->data, totalElements * sizeof(double));

    return copy;
}

double *getRow(const Matrix *matrix, int rowIndex)
{
    checkMatrix(matrix); // Ensure the matrix is valid

    if (rowIndex < 0 || rowIndex >= matrix->rows)
    {
    }

    // Allocate memory for the row
    double *row = (double *)calloc(matrix->cols, sizeof(double));
    if (!row)
    {
    }

    // Copy the elements of the row
    for (int j = 0; j < matrix->cols; j++)
    {
        row[j] = MATRIX_AT_PTR(matrix, rowIndex, j);
    }

    return row;
}

/**
 * @brief Extracts the n-th column of a matrix as a dynamically allocated array.
 *
 * @param[in] matrix Pointer to the input matrix.
 * @param[in] colIndex The index of the column to extract (0-based).
 * @return double* A dynamically allocated array containing the column elements.
 *
 * @note The caller is responsible for freeing the returned array.
 */
double *getColumn(const Matrix *matrix, int colIndex)
{
    checkMatrix(matrix); // Ensure the matrix is valid

    if (colIndex < 0 || colIndex >= matrix->cols)
    {
    }

    // Allocate memory for the column
    double *column = (double *)calloc(matrix->rows, sizeof(double));
    if (!column)
    {
    }

    // Copy the elements of the column
    for (int i = 0; i < matrix->rows; i++)
    {
        column[i] = MATRIX_AT_PTR(matrix, i, colIndex);
    }

    return column;
}
