#include <inttypes.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <avr/pgmspace.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
#include "uart.h"
#include "adc.h"
#include "pwm.h"
#include "timer.h"
#include "servo.h"
#include "ringbuffer.h"
#include "Touchscreen.h"

// Touchscreen Interface
extern Interface Touchscreen_Data;
Interface Buffer_Touchscreen_Data;
#define FLAG_REGISTER_MASK 255

/* Beinhaltet die rohen X/Y-Koordinatenpaare */
struct ringbuffer rb_xy;
/* Beinhaltet gültige X/Y-Koordinatenpaare */
struct ringbuffer rb_xyv;
struct ringbuffer rb_v;

uint8_t stehtcnt = 0;

float last_sx = 0.0;
float last_sy = 0.0;

uint16_t servo_init_x = 1584;
uint16_t servo_init_y = 1458;
uint16_t servo_null_x = servo_init_x;
uint16_t servo_null_y = servo_init_y;

uint16_t destX = 290;
uint16_t destY = 290;

// Touchscreen helper function
static unsigned char Recognize_Event(void) {
    /* disable interrupts */
    cli();

    // Read Data
    Buffer_Touchscreen_Data = Touchscreen_Data;
    // Mask Flag_Register
    Buffer_Touchscreen_Data.Flag_Register &= FLAG_REGISTER_MASK;
    // Clear Joblist
    Touchscreen_Data.Flag_Register ^= Buffer_Touchscreen_Data.Flag_Register;

    sei();
    return Buffer_Touchscreen_Data.Flag_Register;
}

// Sign function
static int sgn(float val) {
    if (val == 0.0)
        return 0;
    if (val > 0.0)
        return 1;
    return -1;
}

// Maximum function
static uint8_t max(uint8_t x, uint8_t y) {
    return x > y ? x : y;
}

// Distance function
static uint8_t distance(uint8_t x, uint8_t y, uint8_t x2, uint8_t y2) {
    return max(abs(x - x2), abs(y - y2));
}

// Controls the balancing of the ball. Returns:
// 1  - if ball is balanced
// -1 - invalid position
// 0  - otherwise
static int control(uint16_t x, uint16_t y) {
    rb_append(&rb_xy, x, y);
    if (rb_xy.count < 10)
        return 0;

    /* Abweichung des jetztigen Werts zu den letzten gespeicherten Werten
     * vergleichen, bei zu großer Abweichung wird der Wert nicht verarbeitet
     * (aber gespeichert). */
    uint16_t avrg = 0;
    uint8_t current = rb_xy.current;
    uint8_t count = 0;
    for (count = 0; count < 10; count++) {
        current = (current == 0 ? 10-1 : current-1);
        avrg += distance(x, y, rb_xy.val_x[current], rb_xy.val_y[current]);
    }
    if ((avrg / 9) >= 75)
        return -1;

    /* Wenn sich die Kugelposition für eine halbe Sekunde ein bisschen nicht ändert,
     * hat sich die Kugel balanciert. */
    if (avrg <= 10) {
        stehtcnt++;

        if (stehtcnt == 30) {
            // Ball is balanced
            servo_null_x = last_sx;
            servo_null_y = last_sy;

            uart_puts("# x ");
            uart_puti(servo_null_x);
            uart_puts("# y ");
            uart_puti(servo_null_y);

            return 1;
        }
    } else {
        stehtcnt = 0;
    }

    rb_append(&rb_xyv, x, y);
    if (rb_xyv.count < 10)
        return 0;

    /* Wir greifen auf den fünftletzten Eintrag (vor dem aktuell eingefügten)
     * zu, indem wir 6 Schritte zurückgehen */
    int8_t xyv_current = rb_xyv.current - 6;
    if (xyv_current < 0) xyv_current += 10;
    float vx = ((int16_t)x - (int16_t)rb_xyv.val_x[xyv_current]) * 1.0/5.0;
    float vy = ((int16_t)y - (int16_t)rb_xyv.val_y[xyv_current]) * 1.0/5.0;
    vx = (vx > 5 ? 5 : (vx < -5 ? -5 : vx));
    vy = (vy > 5 ? 5 : (vy < -5 ? -5 : vy));

    rb_append(&rb_v, vx, vy);
    if (rb_v.count < 10) return 0;

    int16_t xoff = destX - x;
    int16_t yoff = destY - y;

    float servo_x = servo_null_x + (xoff * 0.8 - vx * 32);
    float servo_y = servo_null_y + (yoff * 0.8 - vy * 32);

    /* Entgegenkippen zum leichten Abbremsen */
    if (sgn(xoff) == sgn(vx) && (0.00005 * vx * vx) <= fabsf(xoff))
        servo_x = servo_x + sgn(vx) * 10;
    if (sgn(yoff) == sgn(vy) && (0.00005 * vy * vy) <= fabsf(yoff))
        servo_y = servo_y + sgn(vy) * 10;

    if (last_sx > 0.0) {
        /* Servo-Werte deckeln (maximal 20 Servoschritte pro Messung) */
        if (fabsf(last_sx - servo_x) > 20)
            servo_x = last_sx - sgn(last_sx - servo_x) * 20.0;
        if (fabsf(last_sy - servo_y) > 20)
            servo_y = last_sy - sgn(last_sy - servo_y) * 20.0;
    }
    last_sx = servo_x;
    last_sy = servo_y;

    setServo(0, (int)servo_x);
    setServo(1, (int)servo_y);
    return 0;
}

static int readCommand() {
    destX = 0;
    destY = 0;

    char sign = uart_getc();
    if (sign == '!') {
        servo_null_x = servo_init_x;
        servo_null_y = servo_init_y;
    }

    int i;
    char c;
    for (i = 0; i < 3; i++) {
        c = uart_getc();
        uint16_t d = c - '0';
        destX += d * pow(10, 2 - i);
    }
    c = uart_getc(); // Get comma
    for (i = 0; i < 3; i++) {
        c = uart_getc();
        uint16_t d = c - '0';
        destY += d * pow(10, 2 - i);
    }

    return 1;
}

static int sendResponse(char sign, int16_t x, int16_t y) {
    uart_putc(sign);
    
    if (x < 100) uart_putc('0');
    if (x < 10) uart_putc('0');
    uart_puti(x);

    uart_putc(',');
    
    if (y < 100) uart_putc('0');
    if (y < 10) uart_putc('0');
    uart_puti(y);

    return 1;
}

int main(void) {
    // Initialize ringbuffer
    memset(&rb_xy, '\0', sizeof(struct ringbuffer));
    memset(&rb_xyv, '\0', sizeof(struct ringbuffer));
    memset(&rb_v, '\0', sizeof(struct ringbuffer));
    
    uartInit();
    timerInit();
    servoInit();
    Touchscreen_Init();

    setServo(0, servo_init_x);
    setServo(1, servo_init_y);

    while (1) {
        readCommand();

        while (1) {
            if (!Recognize_Event())
                continue;

            if (!TestBit(Buffer_Touchscreen_Data.Flag_Register, FLAG_REGISTER_COORDINATES))
                continue;
        
            int16_t x = Buffer_Touchscreen_Data.x_pos - 200;
            int16_t y = Buffer_Touchscreen_Data.y_pos - 200;
            int result = control(x, y);

            if (result >= 0) {
                sendResponse(result == 0 ? ':' : '=', x, y);
                if (result != 0) break;
            }
        }
    }

    return 0;
}