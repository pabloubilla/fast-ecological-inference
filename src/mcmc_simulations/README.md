For compiling in mac: 

```
clang -Xpreprocessor -fopenmp \
      -lomp -I/usr/local/include \
      -L/usr/local/lib \
      -o readmat main.c utils_matrix.c cJSON.c
```

And later, running it

```
./readmat pathToJson.json S M
```

On Windows

```
gcc -fopenmp -O2 -o readmat main.c utils_matrix.c cJSON.c
```

After compiling, run the `.sh` script:

```
source run_samples.sh
```

Usually, permissions must be granted for running the script
