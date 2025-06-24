#include "globals.h"
#include <stdbool.h>
#include <stdlib.h>

/**
 * @brief Checks if the matrix is well defined
 *
 * Given a pointer to a matrix, it verifies if the matrix is well alocated and defined and throws an error if
 * there's something wrong.
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

void checkMatrix(const Matrix *m);

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
 */

Matrix createMatrix(int rows, int cols);

/**
 * @brief Liberates the allocated matrix data.
 *
 * @param[in] m The matrix to free the data.
 *
 * @return void Changes to be made on the input matrix and memory.
 *
 */

void freeMatrix(Matrix *m);

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

/**
 * @brief Creates a 4-dimensional matrix.
 *
 * @param[in] dim1 The size of the first dimension.
 * @param[in] dim2 The size of the second dimension.
 * @param[in] dim3 The size of the third dimension.
 * @param[in] dim4 Th size of the fourth dimension.
 *
 * @return int Set of pointers to each dimensional array. This matrix is not from the Matrix struct.
 *
 */

void printMatrix(const Matrix *m);

/**
 * @brief Computes a row-wise sum.
 *
 * Given a matrix, it computes the sum over all the rows and stores them in an array.
 *
 * @param[in] matrix Pointer to the input matrix.
 * @param[out] result Pointer of the resulting array of length `rows`.
 *
 * @return void Written on *result
 *
 * @note
 * - Matrix should be in col-major order
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
 * @brief Computes a column-wise sum.
 *
 * Given a matrix, it computes the sum over all the columns and stores them in an array.
 *
 * @param[in] matrix Pointer to a Matrix structure.
 * @param[out] result Array for the resulting Matrix. It must have the dimensions of the matrix columns.
 *
 * @return void Written on *result
 *
 * @note
 * - Matrix should be in col-major order
 *
 * @warning
 * - The matrix or array pointer may be NULL.
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
 * double result[matrix->cols]
 *
 * colSum(matrix, result);
 * // result now contains [5.0, 7.0, 9.0]
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
 * double matrix[6] = {
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

void fillMatrix(Matrix *matrix, const double value);

/**
 * @brief Checks if the difference of two matrices converge to a value
 *
 * Given two matrices, it performs de absolute difference and evaluate the convergence towards a given
 * arbitrary values: |x1 - x2| < epsilon. If there's a value whom convergence is greater than epsilon, the
 * convergence is not achieved.
 *
 * @param[in] matrix Matrix to perform the substraction.
 * @param[in] matrix Matrix to perform the substraction.
 * @param[in] double Arbitrary value to evaluate the convergence
 *
 * @return bool Boolean value to see if it converges.
 *
 * @warning:
 * - Both matrices should be from the same dimention.
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
 * double values2[6] = {
 * 		1.1, 2.1, 2.9,
 * 		3.9, 5.1, 6.1
 * }
 * Matrix matrix = {
 * .data = values,
 * .rows = 2,
 * .cols = 3
 * }
 *
 * Matrix matrix2 = {
 * .data = values2,
 * .rows = 2,
 * .cols = 3
 * }
 *
 * bool converges = convergeMatrix(matrix, matrix2,  0.02);
 * // bool->true
 * @endcode
 */

/**
 * @brief Retrieves the maximum element of the matrix.
 *
 * @param[in] matrix Matrix to find the maximum element.
 *
 * @return double The maximum element
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
 * double maximum = maxElement(&matrix);
 *
 * // maximum=6.0
 * @endcode
 */

/**
 * @brief Removes the last column of a matrix.
 *
 * @param[in] matrix Pointer to the input matrix.
 * @return Matrix A new matrix with one less column.
 *
 * @note
 * - The original matrix remains unchanged.
 * - The memory for the new matrix is dynamically allocated; remember to free it.
 */

/**
 * @brief Removes the last row of a matrix.
 *
 * @param[in] matrix Pointer to the input matrix.
 * @return Matrix A new matrix with one less row.
 *
 * @note
 * - The original matrix remains unchanged.
 * - The memory for the new matrix is dynamically allocated; remember to free it.
 */

/**
 * @brief Creates a diagonal matrix given a 1D array
 *
 * @param[in] vector Pointer to the array.
 * @param[in] size The size of the array.
 * @return Matrix A new matrix (size x size) with each element of the array as a diagonal.
 *
 * @note
 * - The original array remains unchanged.
 */

/**
 * @brief Computes the inverse of a symmetric positive-definite matrix using Cholesky decomposition.
 *
 * @param[in, out] matrix Pointer to the input matrix (overwritten with the inverse).
 *
 * @note The input matrix must be square and symmetric.
 */

/**
 * @brief Inverts a real symmetric NxN matrix (overwrites the input).
 *
 * Uses an eigen-decomposition (dsyev) to invert A = Q * diag(vals) * Q^T.
 * The input matrix must be square and invertible (no zero eigenvalues).
 *
 * @param[in,out] matrix Pointer to the NxN symmetric matrix in col-major layout.
 */

/**
 * @brief Computes the inverse of a general square matrix using LU decomposition.
 *
 * @param[in, out] matrix Pointer to the input matrix (overwritten with the inverse).
 *
 * @note The input matrix must be square and invertible.
 */

Matrix copMatrix(const Matrix *original);

/**
 * @brief Extracts the n-th row of a matrix as a dynamically allocated array.
 *
 * @param[in] matrix Pointer to the input matrix.
 * @param[in] rowIndex The index of the row to extract (0-based).
 * @return double* A dynamically allocated array containing the row elements.
 *
 * @note The caller is responsible for freeing the returned array.
 */

/**
 * @brief Extracts the n-th column of a matrix as a dynamically allocated array.
 *
 * @param[in] matrix Pointer to the input matrix.
 * @param[in] colIndex The index of the column to extract (0-based).
 * @return double* A dynamically allocated array containing the column elements.
 *
 * @note The caller is responsible for freeing the returned array.
 */

/**
 * @brief Adds a new row to a given matrix by reallocating its memory.
 *
 * The new row is appended to the end of the matrix. The function modifies the
 * input matrix struct in-place.
 *
 * @param[in, out] matrix Pointer to the matrix to which the row will be added.
 * @param[in] newRow Pointer to the array containing the elements of the new row.
 *
 * @return void
 *
 * @note
 * - The newRow must have the same number of elements as the matrix's columns.
 * - The matrix must be valid and well-defined.
 *
 * @example
 * Example usage:
 * @code
 * Matrix m = createMatrix(2, 3); // 2x3 matrix
 * double newRow[3] = {4.0, 5.0, 6.0};
 * addRowToMatrix(&m, newRow);
 * // m is now a 3x3 matrix
 * @endcode
 */

/**
 * @brief Adds a row of zeros at a specific index in a matrix in place.
 *
 * This function modifies the input matrix to add a row of zeros at the specified index.
 *
 * @param[in,out] matrix Pointer to the matrix to modify.
 * @param[in] rowIndex The index where the new row should be added (0-based).
 */

/**
 * @brief Removes a specific row from a matrix in place.
 *
 * This function modifies the input matrix to remove the specified row.
 *
 * @param[in,out] matrix Pointer to the matrix to modify.
 * @param[in] rowIndex The index of the row to remove (0-based).
 */

/**
 * @brief Adds a column of zeros at a specific index in a matrix in place.
 *
 * This function modifies the input matrix to add a column of zeros at the specified index.
 *
 * @param[in,out] matrix Pointer to the matrix to modify.
 * @param[in] colIndex The index where the new column should be added (0-based).
 */

/**
 * @brief Removes a specific column from a matrix in place.
 *
 * This function modifies the input matrix to remove the specified column.
 *
 * @param[in,out] matrix Pointer to the matrix to modify.
 * @param[in] colIndex The index of the column to remove (0-based).
 */

/**
 * @brief Creates a copy of the given Matrix.
 *
 * @param orig Pointer to the original Matrix.
 * @return Pointer to a new Matrix that is a copy of orig.
 *
 * This function uses malloc to allocate memory for both the Matrix struct and its data array.
 * The caller is responsible for freeing the memory (using free) when it is no longer needed.
 */
Matrix *copMatrixPtr(const Matrix *orig);

double *getColumn(const Matrix *matrix, int colIndex);

double *getRow(const Matrix *matrix, int rowIndex);
