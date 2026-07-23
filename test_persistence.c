#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

static inline uint64_t read_timer(void) {
    uint64_t val;
    asm volatile("mrs %0, cntvct_el0" : "=r" (val));
    return val;
}

static inline uint64_t read_timer_freq(void) {
    uint64_t val;
    asm volatile("mrs %0, cntfrq_el0" : "=r" (val));
    return val;
}

void flush_cache_line(volatile int *evict_buf, size_t size) {
    volatile int dummy = 0;
    for (size_t i = 0; i < size; i += 16) {
        dummy += evict_buf[i];
    }
}

void transform_to_shuffled_linked_list(volatile int *array, size_t size) {
    int *indices = malloc(size * sizeof(int));
    for (size_t i = 0; i < size; i++) indices[i] = i;
    
    srand(time(NULL));
    for (size_t i = size - 1; i > 0; i--) {
        size_t j = rand() % (i + 1);
        int temp = indices[i];
        indices[i] = indices[j];
        indices[j] = temp;
    }

    for (size_t i = 0; i < size - 1; i++) array[indices[i]] = indices[i + 1];
    array[indices[size - 1]] = indices[0];
    free(indices);
}

int main() {
    int test_samples = 200;
    size_t array_size = 8 * 1024 * 1024;
    size_t eviction_size = 32 * 1024 * 1024;
    uint64_t timer_freq = read_timer_freq();

    volatile int *array = NULL;
    volatile int *eviction_buffer = NULL;
    posix_memalign((void**)&array, 64, array_size * sizeof(int));
    posix_memalign((void**)&eviction_buffer, 64, eviction_size * sizeof(int));

    for(size_t i = 0; i < eviction_size; i++) eviction_buffer[i] = i;
    transform_to_shuffled_linked_list(array, array_size);

    FILE *file = fopen("data/test_latencies.csv", "w");
    fprintf(file, "Latency,Ground_Truth\n");

    for (int iter = 0; iter < test_samples; iter++) {
        int should_persist = iter % 2; 
        
        uint64_t start_ticks, end_ticks;
        int current_index = 0;
        int batch_size = 10000;

        for (int i = 0; i < batch_size; i++) current_index = array[current_index];

        if (should_persist) {
            flush_cache_line(eviction_buffer, eviction_size);
        }

        asm volatile("isb" ::: "memory");
        start_ticks = read_timer();
        asm volatile("isb" ::: "memory");
        for (int i = 0; i < batch_size; i++) {
            current_index = array[current_index];
        }
        asm volatile("" : : "g"(current_index) : "memory");
        asm volatile("isb" ::: "memory");
        end_ticks = read_timer();
        asm volatile("isb" ::: "memory");

        uint64_t elapsed_ticks = end_ticks - start_ticks;
        uint64_t elapsed_ns = ((elapsed_ticks * 1000000000ULL) / timer_freq) / batch_size;

        if (should_persist) {
            fprintf(file, "%llu,PERSISTED\n", elapsed_ns);
        } else {
            fprintf(file, "%llu,CACHED (VOLATILE)\n", elapsed_ns);
        }
    }

    fclose(file);
    free((void*)array);
    free((void*)eviction_buffer);
    return EXIT_SUCCESS;
}