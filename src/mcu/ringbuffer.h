#include <stdint.h>
#include <stdbool.h>

/* sizeof = 42 */
struct ringbuffer {
    uint8_t count;
    uint8_t current;
    uint16_t val_x[10];
    uint16_t val_y[10];
};

void rb_append(struct ringbuffer *rb, uint16_t x, uint16_t y);
