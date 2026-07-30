#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <string.h>

// Reads the ARM Generic Timer
static inline uint64_t read_timer(void) {
    uint64_t val;
    asm volatile("mrs %0, cntvct_el0" : "=r" (val));
    return val;
}

// Reads the ARM Generic Timer frequency
static inline uint64_t read_timer_freq(void) {
    uint64_t val;
    asm volatile("mrs %0, cntfrq_el0" : "=r" (val));
    return val;
}

// Manually flushes cache lines by writing to a buffer to force eviction
void flush_cache(volatile int *evict_buf, size_t size) {
    for (size_t i = 0; i < size; i += 16) { // Step by typical ARM cache-line sizes (16 ints x 4 bytes = 64 bytes)
        evict_buf[i] = evict_buf[i] + 1;
    }
    asm volatile("dsb sy" ::: "memory");
}

// Transforms an array into a linked list to bypass the Hardware Prefetcher
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
    int test_samples = 1000;
    size_t array_size = 256 * 1024; // 256,000 ints x 4 bytes = 1MB working set (to ensure it fits easily in L2/SLC)
    size_t eviction_size = 64 * 1024 * 1024; // 64MB x 4 bytes = 256MB eviction buffer (large enough to evict all cache)
    
    // Read ARM System Timer Frequency
    uint64_t timer_freq = read_timer_freq();
    if (timer_freq == 0) {
        printf("Failed to determine timer frequency.\n");
        return EXIT_FAILURE;
    }

    // Allocate memory
    volatile int *array = NULL;
    volatile int *eviction_buffer = NULL;
    posix_memalign((void**)&array, 64, array_size * sizeof(int));
    posix_memalign((void**)&eviction_buffer, 64, eviction_size * sizeof(int));

    // Prepare the shuffled linked list
    transform_to_shuffled_linked_list(array, array_size);

    // Open CSV file
    FILE *file = fopen("data/test_latencies.csv", "w");
    fprintf(file, "Latency,Ground_Truth\n");
    printf("Writing test data to 'data/test_latencies'");

    // Measure a sample of latencies to be used as test data for clustering model
    for (int iter = 0; iter < test_samples; iter++) {
        int should_persist = iter % 2; 
        
        uint64_t start_ticks, end_ticks;
        int current_index = 0;
        int batch_size = 10000;

        // Warm-up loop preloads working set into caches and TLB to ensure desired cache behaviour
        for (int i = 0; i < batch_size; i++) current_index = array[current_index];

        // Flush cache lines if measuring main memory latencies
        if (should_persist) {
            flush_cache(eviction_buffer, eviction_size);
        }

        current_index = 0;

        // Measure access times
        asm volatile("isb" ::: "memory");
        start_ticks = read_timer(); // Start timer
        asm volatile("isb" ::: "memory");
        for (int i = 0; i < batch_size; i++) {
            current_index = array[current_index];
        }        
        asm volatile("" : : "g"(current_index) : "memory"); // Prevent compiler optimisation
        asm volatile("isb" ::: "memory");
        end_ticks = read_timer(); // End timer
        asm volatile("isb" ::: "memory");

        // Calculate average of batch measurements
        uint64_t elapsed_ticks = end_ticks - start_ticks;
        uint64_t elapsed_ns = ((elapsed_ticks * 1000000000ULL) / timer_freq) / batch_size;

        if (should_persist) {
            fprintf(file, "%llu,PERSISTED\n", elapsed_ns);
        } else {
            fprintf(file, "%llu,CACHED (VOLATILE)\n", elapsed_ns);
        }
    }

    // Close CSV file
    fclose(file);

    // Free allocated memory
    free((void*)array);
    free((void*)eviction_buffer);

    return EXIT_SUCCESS;
}