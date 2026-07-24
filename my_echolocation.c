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

// Performs cache line flush manually
void flush_cache_line(volatile int *evict_buf, size_t size) {
    volatile int dummy = 0;
    for (size_t i = 0; i < size; i += 16) { 
        dummy += evict_buf[i];
    }
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

void measure_memory_access_times(volatile int *array, size_t array_size, volatile int *evict_buf, size_t evict_size, uint64_t *min_ns, uint64_t *max_ns, uint64_t timer_freq, volatile uint64_t *latency_buffer, int iteration) {
    uint64_t start_ticks, end_ticks;
    
    static int current_index = 0; 
    int start_index = current_index; // Maintain the starting index for the measurement loop
    int batch_size = 10000;

    // Warm-up loop to ensure data is stored in cache
    for (int i = 0; i < batch_size; i++) {
        current_index = array[current_index];
    }

    // Alternate between flushing the cache (resulting in main memory access)
    // And skipping the cache flush (resulting in probable cache hit)
    int should_flush = iteration % 2;
    if (should_flush) {
        flush_cache_line(evict_buf, evict_size);
    }

    // Reset index back to where the warm-up loop started to measure the exact same elements
    // To keep the warm-up and measurement loops symmetrical
    current_index = start_index;

    // Measure how long a batch of reads takes
    asm volatile("isb" ::: "memory");
    start_ticks = read_timer(); // Start timer
    asm volatile("isb" ::: "memory");
    for (int i = 0; i < batch_size; i++) {
        current_index = array[current_index];
    }
    asm volatile("" : : "g"(current_index) : "memory"); // Prevent compiler optimisation from deleting or reordering the whole loop
    asm volatile("isb" ::: "memory");
    end_ticks = read_timer(); // Stop timer
    asm volatile("isb" ::: "memory");

    // Calculate the average access time
    uint64_t elapsed_ticks = end_ticks - start_ticks;
    uint64_t elapsed_ns = ((elapsed_ticks * 1000000000ULL) / timer_freq) / batch_size;

    // Update min and max access times
    if (elapsed_ns < *min_ns) *min_ns = elapsed_ns;
    if (elapsed_ns > *max_ns) *max_ns = elapsed_ns;

    // Append access times array with measured average latency
    latency_buffer[iteration] = elapsed_ns;
}

int main() {
    size_t array_size = 8 * 1024 * 1024; // 32MB - large enough to exceed potentially large cache sizes
    size_t eviction_size = 32 * 1024 * 1024; // 128MB eviction buffer
    int total_iterations = 5000;
    uint64_t min_ns = UINT64_MAX, max_ns = 0;

    uint64_t timer_freq = read_timer_freq();
    if (timer_freq > 0) {
        printf("ARM System Timer Frequency: %llu Hz (%.2f MHz)\n", timer_freq, timer_freq / 1000000.0);
    }
    else {
        printf("Failed to determine timer frequency.\n");
        return EXIT_FAILURE;
    }

    volatile int *array = NULL;
    volatile int *eviction_buffer = NULL;
    volatile uint64_t *latency_buffer = NULL;
    
    if (posix_memalign((void**)&array, 64, array_size * sizeof(int)) != 0) return EXIT_FAILURE;
    if (posix_memalign((void**)&eviction_buffer, 64, eviction_size * sizeof(int)) != 0) return EXIT_FAILURE;
    if (posix_memalign((void**)&latency_buffer, 64, total_iterations * sizeof(uint64_t)) != 0) return EXIT_FAILURE;

    for(size_t i = 0; i < eviction_size; i++) eviction_buffer[i] = i;
    for (int i = 0; i < total_iterations; i++) latency_buffer[i] = 0;

    transform_to_shuffled_linked_list(array, array_size);
    
    for (int i = 0; i < total_iterations; i++) {
        measure_memory_access_times(array, array_size, eviction_buffer, eviction_size, &min_ns, &max_ns, timer_freq, latency_buffer, i);
    }

    printf("Minimum Access Time: %llu ns\n", min_ns);
    printf("Maximum Access Time: %llu ns\n", max_ns);

    printf("Writing data to data/access_times.csv\n");
    FILE *file = fopen("data/access_times.csv", "w");
    if (file) {
        fprintf(file, "Latency\n");
        for (int i = 0; i < total_iterations; i++) {
            fprintf(file, "%llu\n", latency_buffer[i]);
        }
        fclose(file);
    }

    free((void *)array);
    free((void *)eviction_buffer);
    free((void *)latency_buffer);
    return EXIT_SUCCESS;
}