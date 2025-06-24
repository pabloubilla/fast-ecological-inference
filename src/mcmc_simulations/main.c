#include "cJSON.h"
#include "globals.h"
#include "uthash.h"
#include "utils_matrix.h"
#include <math.h>
#include <omp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h> // for time()
//
typedef struct
{
    uint32_t b;
    Matrix **data;
    int *counts;
    size_t size;
} OmegaSet;
// ---...--- //

// ---- Macro for finding the minimum ---- //
#define MIN(a, b) ((a) < (b) ? (a) : (b))
#define MAX(a, b) ((a) > (b) ? (a) : (b))

uint32_t TOTAL_VOTES = 0;
uint32_t TOTAL_BALLOTS = 0;
uint16_t TOTAL_CANDIDATES = 0;
uint16_t TOTAL_GROUPS = 0;
uint16_t *BALLOTS_VOTES = NULL;    // Total votes per ballot
uint32_t *CANDIDATES_VOTES = NULL; // Total votes per candidate
uint32_t *GROUP_VOTES = NULL;      // Total votes per group
double *inv_BALLOTS_VOTES = NULL;  // BALLOTS_VOTES^{-1}
Matrix *X = NULL;
Matrix *W = NULL;
OmegaSet **OMEGASET = NULL; // Global pointer to store all H sets

#define Q_3D(q, bIdx, gIdx, cIdx, G, C) ((q)[(bIdx) * (G) * (C) + (cIdx) * (G) + (gIdx)])
#define MATRIX_AT(matrix, i, j) (matrix.data[(j) * (matrix.rows) + (i)])
#define MATRIX_AT_PTR(matrix, i, j) (matrix->data[(j) * (matrix->rows) + (i)])

void saveOmegaSetToJSON(const char *filename)
{
    // Create the root JSON array
    cJSON *root = cJSON_CreateArray();
    if (!root)
    {
        fprintf(stderr, "Failed to create JSON root array\n");
        return;
    }

    // For each ballot b
    for (uint32_t b = 0; b < TOTAL_BALLOTS; b++)
    {
        OmegaSet *set = OMEGASET[b];
        // Create JSON array for this ballot’s matrices
        cJSON *matrices_array = cJSON_CreateArray();
        if (!matrices_array)
        {
            goto cleanup;
        }

        // For each sample s in the OmegaSet
        for (size_t s = 0; s < set->size; s++)
        {
            Matrix *mat = set->data[s];
            // Create JSON array-of-arrays for this single matrix
            cJSON *mat_json = cJSON_CreateArray();
            if (!mat_json)
            {
                goto cleanup;
            }

            // Fill rows
            for (int g = 0; g < mat->rows; g++)
            {
                cJSON *row_json = cJSON_CreateArray();
                if (!row_json)
                {
                    goto cleanup;
                }
                for (int c = 0; c < mat->cols; c++)
                {
                    double v = MATRIX_AT_PTR(mat, g, c);
                    cJSON_AddItemToArray(row_json, cJSON_CreateNumber(v));
                }
                cJSON_AddItemToArray(mat_json, row_json);
            }
            // Add this matrix to the matrices array
            cJSON_AddItemToArray(matrices_array, mat_json);
        }

        // Wrap with object to tag which ballot b this is (optional)
        cJSON *ballot_obj = cJSON_CreateObject();
        if (!ballot_obj)
        {
            goto cleanup;
        }
        cJSON_AddNumberToObject(ballot_obj, "b", b);
        cJSON_AddItemToObject(ballot_obj, "matrices", matrices_array);

        // Append to root
        cJSON_AddItemToArray(root, ballot_obj);
    }

    // Print to file
    char *out = cJSON_Print(root);
    if (out)
    {
        FILE *f = fopen(filename, "w");
        if (f)
        {
            fprintf(f, "%s\n", out);
            fclose(f);
        }
        else
        {
            fprintf(stderr, "Error opening %s for writing\n", filename);
        }
        free(out);
    }

cleanup:
    cJSON_Delete(root);
    printf("OmegaSet saved to JSON %s\n", filename);
}

int lessThanColRow(Matrix mat, int b, int g, int c, int candidateVotes, int groupVotes)
{
    int groupSum = 0;
    int canSum = 0;
    for (uint16_t i = 0; i < TOTAL_GROUPS; i++)
    {
        canSum += MATRIX_AT(mat, i, c);
    }
    for (uint16_t j = 0; j < TOTAL_CANDIDATES; j++)
    {
        groupSum += MATRIX_AT(mat, g, j);
    }
    int slackC = candidateVotes - canSum;
    int slackG = groupVotes - groupSum;

    return MIN(slackC, slackG);
}

void allocateRandoms(int M, int S, uint8_t **c1, uint8_t **c2, uint8_t **g1, uint8_t **g2)
{
    uint32_t size = M * S;

    // Correct sizeof usage in calloc
    *c1 = (uint8_t *)calloc(size, sizeof(uint8_t));
    *c2 = (uint8_t *)calloc(size, sizeof(uint8_t));
    *g1 = (uint8_t *)calloc(size, sizeof(uint8_t));
    *g2 = (uint8_t *)calloc(size, sizeof(uint8_t));

    if (!*c1 || !*c2 || !*g1 || !*g2)
    {
        fprintf(stderr, "Memory allocation failed in allocateRandoms.\n");
        exit(EXIT_FAILURE);
    }

    // Initialize RNG if not done yet (can also be in main())
    srand((unsigned int)time(NULL));

    int allow_repeat = (TOTAL_CANDIDATES <= 1 || TOTAL_GROUPS <= 1);

    for (uint32_t i = 0; i < size; i++)
    {
        // No need to check interrupt in pure C
        (*c1)[i] = (uint8_t)(rand() % TOTAL_CANDIDATES);
        (*g1)[i] = (uint8_t)(rand() % TOTAL_GROUPS);

        do
        {
            (*c2)[i] = (uint8_t)(rand() % TOTAL_CANDIDATES);
            (*g2)[i] = (uint8_t)(rand() % TOTAL_GROUPS);
        } while (!allow_repeat && ((*c2)[i] == (*c1)[i] || (*g2)[i] == (*g1)[i]));
    }
}

Matrix startingPoint3(int b)
{
    // ---- Retrieve the initial variables ---- //
    Matrix toReturn = createMatrix(TOTAL_GROUPS, TOTAL_CANDIDATES);
    double *groupVotes = getRow(W, b);
    double *candidateVotes = getColumn(X, b);

    // ---- Calculate the expected value ---- //
    double totalC = 0;
    double totalG = 0;
    for (uint16_t g = 0; g < TOTAL_GROUPS; g++)
    {
        for (uint16_t c = 0; c < TOTAL_CANDIDATES; c++)
        {
            double mult = groupVotes[g] * candidateVotes[c];

            if (g == 0)
                totalC += candidateVotes[c];

            // In case of mismatch, we divide for the maximum

            MATRIX_AT(toReturn, g, c) = mult;
        }
        totalG += groupVotes[g];
    }
    // ---...--- //

    // ---- Division for mismatchs ---- //
    double divide = MAX(BALLOTS_VOTES[b], totalC);
    divide = MAX(divide, totalG);

    for (uint16_t g = 0; g < TOTAL_GROUPS; g++)
    {
        for (uint16_t c = 0; c < TOTAL_CANDIDATES; c++)
        {
            double newValue = MATRIX_AT(toReturn, g, c) / divide;
            double floored = floor(newValue);
            MATRIX_AT(toReturn, g, c) = floored;
        }
    }

    for (uint16_t g = 0; g < TOTAL_GROUPS; g++)
    {

        for (uint16_t c = 0; c < TOTAL_CANDIDATES; c++)
        {
            int groupRestriction = groupVotes[g];
            int candidateRestriction = candidateVotes[c];

            int m = lessThanColRow(toReturn, b, g, c, candidateRestriction, groupRestriction);
            if (m > 0)
            {
                MATRIX_AT(toReturn, g, c) += m;
            }
        }
    }
    // ---...--- //

    // ---...--- //
    free(groupVotes);
    free(candidateVotes);
    return toReturn;
}

void generateOmegaSet(int M, int S)
{
#ifdef _OPENMP
#pragma omp parallel
    {
        if (omp_get_thread_num() == 0)
        {
            int num_threads = omp_get_num_threads();
            printf("[OpenMP] Parallelism active with %d threads\n", num_threads);
        }
    }
#else
    printf("[OpenMP] NOT enabled (compiled without -fopenmp)\n");
#endif
    // ---- Allocate memory for the `b` index ----
    OMEGASET = calloc(TOTAL_BALLOTS, sizeof(OmegaSet *));
    uint8_t *c1 = NULL;
    uint8_t *c2 = NULL;
    uint8_t *g1 = NULL;
    uint8_t *g2 = NULL;

    uint32_t arraySize = M * S;

    allocateRandoms(M, S, &c1, &c2, &g1, &g2);
    // Compute the partition size
    int partitionSize = M / TOTAL_BALLOTS;
    if (partitionSize == 0)
        partitionSize = 1; // Prevent division by zero in extreme cases

// ---- Perform the main iterations ---- //
#ifdef _OPENMP
#pragma omp parallel for
#endif
    for (uint32_t b = 0; b < TOTAL_BALLOTS; b++)
    { // ---- For every ballot box
        // ---- Define a seed, that will be unique per thread ----
        //    unsigned int seed = rand_r(&seedNum) + omp_get_thread_number();
        // ---- Allocate memory for the OmegaSet ---- //
        OMEGASET[b] = calloc(1, sizeof(OmegaSet));
        OMEGASET[b]->b = b;
        OMEGASET[b]->size = S;
        OMEGASET[b]->data = calloc(S, sizeof(Matrix *));
        // ---...--- //
        // ---- The `base` element used as a starting point ----
        Matrix startingZ = startingPoint3(b);
        if (b % 5 == 0)
        {
            int totalVals = 0;
            for (int g = 0; g < TOTAL_GROUPS; g++)
            {
                for (int c = 0; c < TOTAL_CANDIDATES; c++)
                {
                    totalVals += MATRIX_AT(startingZ, g, c);
                }
            }
        }
        int ballotShift = floor(((double)b / TOTAL_BALLOTS) * (M * S));

        // Impose the first step
        Matrix *append = calloc(1, sizeof(Matrix));
        *append = copMatrix(&startingZ);
        OMEGASET[b]->data[0] = append;
        freeMatrix(&startingZ);

        for (int s = 1; s < S; s++)
        { // --- For each sample given a ballot box
            // TODO: El sampling debe hacerse de tamaño M*S
            // ---- Copy the initial matrix ----
            Matrix *pastMatrix = OMEGASET[b]->data[s - 1];
            Matrix steppingZ = copMatrix(pastMatrix);
            for (int m = 0; m < M; m++)
            { // --- For each step size given a sample and a ballot box
                // ---- Sample random indexes ---- //
                int shiftIndex = (s * M + ballotShift + m) % (M * S);
                uint8_t randomCDraw = c1[shiftIndex];
                uint8_t randomCDraw2 = c2[shiftIndex];
                uint8_t randomGDraw = g1[shiftIndex];
                uint8_t randomGDraw2 = g2[shiftIndex];

                // decode(randomCDraw, TOTAL_CANDIDATES, &c1, &c2);
                //  decode(randomGDraw, TOTAL_GROUPS, &g1, &g2);

                // ---- Check non negativity condition ---- //
                double firstSubstraction = MATRIX_AT(steppingZ, randomGDraw, randomCDraw);
                double secondSubstraction = MATRIX_AT(steppingZ, randomGDraw2, randomCDraw2);

                if (firstSubstraction <= 0 || secondSubstraction <= 0)
                    continue;
                // ---...--- //

                // ---- Asign changes on the new matrix ---- //
                MATRIX_AT(steppingZ, randomGDraw, randomCDraw) -= 1;
                MATRIX_AT(steppingZ, randomGDraw2, randomCDraw2) -= 1;
                MATRIX_AT(steppingZ, randomGDraw, randomCDraw2) += 1;
                MATRIX_AT(steppingZ, randomGDraw2, randomCDraw) += 1;
                //  ---...--- //
            } // --- End the step size loop
            // ---- Add the combination to the OmegaSet ---- //
            Matrix *append = calloc(1, sizeof(Matrix));
            *append = copMatrix(&steppingZ);
            OMEGASET[b]->data[s] = append;
            freeMatrix(&steppingZ);
            // ---...--- //
        } // --- End the sample loop
        // freeMatrix(&startingZ);
    } // --- End the ballot box loop
    free(c1);
    free(c2);
    free(g1);
    free(g2);
}

void setParameters(Matrix *xCPP, Matrix *wCPP)
{
    // Must generate a copy because of R's gc() in c++

    Matrix *x = copMatrixPtr(xCPP);
    Matrix *w = copMatrixPtr(wCPP);

    // ---- Validation checks ---- //
    // ---- Check if there's a NULL pointer ----
    if (!x->data || !w->data)
    {
    }

    // ---- Check for dimentional coherence ----
    if (x->cols != w->rows && x->cols > 0)
    {
    }

    // ---- Allocate memory for the global variables ---- //
    // ---- Since they're integers it will be better to operate with integers rather than a cBLAS operations (since it
    // receives doubles) ----
    TOTAL_CANDIDATES = x->rows;
    TOTAL_GROUPS = w->cols;
    TOTAL_BALLOTS = w->rows;
    CANDIDATES_VOTES = (uint32_t *)calloc(TOTAL_CANDIDATES, sizeof(int32_t));
    GROUP_VOTES = (uint32_t *)calloc(TOTAL_GROUPS, sizeof(uint32_t));
    BALLOTS_VOTES = (uint16_t *)calloc(TOTAL_BALLOTS, sizeof(uint16_t));
    inv_BALLOTS_VOTES = (double *)calloc(TOTAL_BALLOTS, sizeof(double));

    // ---- Allocate memory for the matrices
    X = calloc(1, sizeof(Matrix));
    *X = createMatrix(x->rows, x->cols);
    memcpy(X->data, x->data, sizeof(double) * x->rows * x->cols);

    W = calloc(1, sizeof(Matrix));
    *W = createMatrix(w->rows, w->cols);
    memcpy(W->data, w->data, sizeof(double) * w->rows * w->cols);
    // ---...--- //

    // ---- Fill the variables ---- //
    for (uint32_t b = 0; b < TOTAL_BALLOTS; b++)
    { // --- For each ballot box

        for (uint16_t c = 0; c < TOTAL_CANDIDATES; c++)
        { // --- For each candidate given a ballot box
            // ---- Add the candidate votes, ballot votes and total votes ----
            CANDIDATES_VOTES[c] += (uint32_t)MATRIX_AT_PTR(X, c, b);
            TOTAL_VOTES += (uint32_t)MATRIX_AT_PTR(
                X, c, b); // Usually, TOTAL_CANDIDATES < TOTAL_GROUPS, hence, it's better to make less sums.
            BALLOTS_VOTES[b] += (uint16_t)MATRIX_AT_PTR(X, c, b);
        } // --- End candidate loop

        for (uint16_t g = 0; g < TOTAL_GROUPS; g++)
        { // --- For each group given a ballot box
            // ---- Add the group votes ----
            GROUP_VOTES[g] += (uint32_t)MATRIX_AT_PTR(W, b, g);
        } // --- End group loop

        // ---- Compute the inverse of the ballot votes, at this point the `b` votes are ready ----
        inv_BALLOTS_VOTES[b] = 1.0 / (double)BALLOTS_VOTES[b];
    } // --- End ballot box loop
}

// Reads matrix and stores in column-major format
double *read_matrix_colmajor(cJSON *matrix_json, size_t *nrow, size_t *ncol)
{
    if (!cJSON_IsArray(matrix_json))
    {
        fprintf(stderr, "Expected JSON array for matrix.\n");
        return NULL;
    }

    *nrow = cJSON_GetArraySize(matrix_json);
    if (*nrow == 0)
    {
        *ncol = 0;
        return NULL;
    }

    cJSON *first_row = cJSON_GetArrayItem(matrix_json, 0);
    if (!cJSON_IsArray(first_row))
    {
        fprintf(stderr, "Expected array of arrays (matrix rows).\n");
        return NULL;
    }

    *ncol = cJSON_GetArraySize(first_row);
    double *matrix = malloc((*nrow) * (*ncol) * sizeof(double));
    if (!matrix)
    {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    // Fill col-major array
    for (size_t i = 0; i < *nrow; i++)
    {
        cJSON *row = cJSON_GetArrayItem(matrix_json, i);
        if (!cJSON_IsArray(row))
        {
            fprintf(stderr, "Non-array row at index %zu\n", i);
            free(matrix);
            return NULL;
        }
        if (cJSON_GetArraySize(row) != *ncol)
        {
            fprintf(stderr, "Inconsistent column count in row %zu\n", i);
            free(matrix);
            return NULL;
        }

        for (size_t j = 0; j < *ncol; j++)
        {
            cJSON *val = cJSON_GetArrayItem(row, j);
            if (!cJSON_IsNumber(val))
            {
                fprintf(stderr, "Non-numeric value at (%zu, %zu)\n", i, j);
                free(matrix);
                return NULL;
            }
            matrix[j * (*nrow) + i] = val->valuedouble;
        }
    }

    return matrix;
}

char *read_file(const char *filename)
{
    FILE *fp = fopen(filename, "rb");
    if (!fp)
    {
        perror("fopen");
        exit(EXIT_FAILURE);
    }
    fseek(fp, 0, SEEK_END);
    long len = ftell(fp);
    rewind(fp);

    char *content = malloc(len + 1);
    fread(content, 1, len, fp);
    content[len] = '\0';
    fclose(fp);
    return content;
}

int main(int argc, char **argv)
{
    if (argc != 4)
    {
        fprintf(stderr, "Usage: %s path_to_json S M\n", argv[0]);
        return 1;
    }

    const char *json_path = argv[1];
    int S = atoi(argv[2]); // samples
    int M = atoi(argv[3]); // steps

    if (S <= 0 || M <= 0)
    {
        fprintf(stderr, "S and M must be positive integers.\n");
        return 1;
    }

    // Read JSON file
    char *json_str = read_file(json_path);
    cJSON *root = cJSON_Parse(json_str);
    free(json_str);

    if (!root)
    {
        fprintf(stderr, "JSON parsing failed.\n");
        return 1;
    }

    // Parse X
    cJSON *X_json = cJSON_GetObjectItemCaseSensitive(root, "X");
    size_t X_nrow, X_ncol;
    double *X_data = read_matrix_colmajor(X_json, &X_nrow, &X_ncol);
    if (!X_data)
    {
        cJSON_Delete(root);
        return 1;
    }
    Matrix mx = {.data = X_data, .rows = (int)X_nrow, .cols = (int)X_ncol};

    // Parse W
    cJSON *W_json = cJSON_GetObjectItemCaseSensitive(root, "W");
    size_t W_nrow, W_ncol;
    double *W_data = read_matrix_colmajor(W_json, &W_nrow, &W_ncol);
    if (!W_data)
    {
        free(X_data);
        cJSON_Delete(root);
        return 1;
    }
    Matrix mw = {.data = W_data, .rows = (int)W_nrow, .cols = (int)W_ncol};

    // Debug info
    printf("Matrix X: %d x %d\n", mx.rows, mx.cols);
    printf("Matrix W: %d x %d\n", mw.rows, mw.cols);
    printf("Generating OmegaSet with M = %d, S = %d\n", M, S);

    // Set global parameters and data
    setParameters(&mx, &mw);

    // Generate the OmegaSet
    generateOmegaSet(M, S);
    saveOmegaSetToJSON("omegaset.json");

    // Free temporary JSON-parsed matrix data
    free(X_data);
    free(W_data);
    cJSON_Delete(root);
    return 0;
}
