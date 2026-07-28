#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <time.h>

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

// Transforms a subset of the array into a linked list to bypass the Hardware Prefetcher
void transform_to_shuffled_linked_list(volatile int *array, size_t num_elements) {
    int *indices = malloc(num_elements * sizeof(int));
    if (!indices) {
        perror("Failed to allocate indices");
        exit(EXIT_FAILURE);
    }
    
    for (size_t i = 0; i < num_elements; i++) {
        indices[i] = (int)i;
    }
    
    // Shuffle the array elements
    srand((unsigned int)time(NULL));
    for (size_t i = num_elements - 1; i > 0; i--) {
        size_t j = (size_t)rand() % (i + 1);
        int temp = indices[i];
        indices[i] = indices[j];
        indices[j] = temp;
    }

    // Link the shuffled indices to form a cyclic list
    for (size_t i = 0; i < num_elements - 1; i++) {
        array[indices[i]] = indices[i + 1];
    }
    array[indices[num_elements - 1]] = indices[0];
    
    free(indices);
}

// Measures a batch of access times and calculates the average
static inline uint64_t measure_batch_latency(volatile int *array, int *current_index, int batch_size, uint64_t timer_freq) {
    asm volatile("isb" ::: "memory");
    uint64_t start_ticks = read_timer(); // Start timer
    asm volatile("isb" ::: "memory");
    
    int idx = *current_index;
    for (int i = 0; i < batch_size; i++) {
        idx = array[idx];
    }
    *current_index = idx;
    
    asm volatile("" : : "g"(*current_index) : "memory"); // Prevent compiler optimisation
    asm volatile("isb" ::: "memory");
    uint64_t end_ticks = read_timer(); // End timer
    asm volatile("isb" ::: "memory");
    
    // Calculate average of batch measurements
    uint64_t elapsed_ticks = end_ticks - start_ticks;
    return ((elapsed_ticks * 1000000000ULL) / timer_freq) / (uint64_t)batch_size;
}

// Measures access times for a specific array size
uint64_t benchmark_array_size(volatile int *array, size_t current_bytes, int batch_size, 
                             int iterations_per_size, uint64_t timer_freq, FILE *file, 
                             uint64_t *min_latency, uint64_t *max_latency) {
    size_t num_elements = current_bytes / sizeof(int);
    
    // Prepare the shuffled linked list
    transform_to_shuffled_linked_list(array, num_elements);

    int current_index = 0;
    uint64_t total_latency_ns = 0;

    // Warm-up loop preloads working set into caches and TLB to ensure desired cache behaviour
    for (size_t i = 0; i < num_elements; i++) {
        current_index = array[current_index];
    }

    // Measure access times
    for (int t = 0; t < iterations_per_size; t++) {
        uint64_t elapsed_ns = measure_batch_latency(array, &current_index, batch_size, timer_freq);

        // Update global min and max latency values
        if (elapsed_ns < *min_latency) *min_latency = elapsed_ns;
        if (elapsed_ns > *max_latency) *max_latency = elapsed_ns;
        
        // Write access time to CSV
        fprintf(file, "%zu,%llu\n", current_bytes, elapsed_ns);
        total_latency_ns += elapsed_ns;
    }

    return total_latency_ns / (uint64_t)iterations_per_size;
}

int main(void) {
    size_t min_bytes = 4 * 1024; // Start at 4KB
    size_t max_bytes = 64 * 1024 * 1024; // Sweep up to 64MB (inclusive)
    int batch_size = 10000; // Latency measurements per batch
    int iterations_per_size = 50000; // Measurements per array size

    uint64_t min_latency_ns = UINT64_MAX;
    uint64_t max_latency_ns = 0;
    
    // Read ARM System Timer Frequency
    uint64_t timer_freq = read_timer_freq();
    if (timer_freq == 0) {
        printf("Failed to determine timer frequency.\n");
        return EXIT_FAILURE;
    }
    printf("ARM System Timer Frequency: %llu Hz (%.2f MHz)\n", timer_freq, (double)timer_freq / 1000000.0);

    // Allocate benchmark buffer once to reuse it
    volatile int *array = NULL;
    if (posix_memalign((void**)&array, 64, max_bytes) != 0) {
        perror("Memory allocation failed");
        return EXIT_FAILURE;
    }

    // Open CSV file
    printf("Writing latencies to 'data/access_times.csv'...");
    FILE *file = fopen("data/access_times.csv", "w");
    if (!file) {
        perror("Failed to open file 'data/access_times.csv'");
        free((void *)array);
        return EXIT_FAILURE;
    }
    
    fprintf(file, "Array_Size_Bytes,Latency\n");
    printf("\n%-20s | %-15s", "Array Size", "Average Latency");
    printf("\n---------------------------------------------");

    // Measure and record access times for each array size
    for (size_t current_bytes = min_bytes; current_bytes <= max_bytes; current_bytes *= 2) {
        uint64_t avg_latency_ns = benchmark_array_size(
            array, current_bytes, batch_size, iterations_per_size, 
            timer_freq, file, &min_latency_ns, &max_latency_ns
        );

        // Output the average access times per array size to the console
        if (current_bytes < 1024 * 1024) {
            printf("\n%4zu KB               | %3llu ns", current_bytes / 1024, avg_latency_ns);
        } else {
            printf("\n%4zu MB               | %3llu ns", current_bytes / (1024 * 1024), avg_latency_ns);
        }
    }
    printf("\n---------------------------------------------");

    fclose(file); // Close CSV file
    free((void *)array); // Free allocated memory

    printf("\nMinimum Access Time: %llu ns", min_latency_ns);
    printf("\nMaximum Access Time: %llu ns", max_latency_ns);
    printf("\nLatency gathering complete.\n");

    return EXIT_SUCCESS;
}