/*
 * GPIO driver for LPC2361 (Fast GPIO)
 */

#include "gpio.h"
#include "lpc2361.h"
#include "config.h"
#include "utils/debug.h"

// Fast GPIO register base addresses
static volatile uint32_t * const fio_dir[]  = {&FIO0DIR, &FIO1DIR, &FIO2DIR, &FIO3DIR, &FIO4DIR};
static volatile uint32_t * const fio_set[]  = {&FIO0SET, &FIO1SET, &FIO2SET, &FIO3SET, &FIO4SET};
static volatile uint32_t * const fio_clr[]  = {&FIO0CLR, &FIO1CLR, &FIO2CLR, &FIO3CLR, &FIO4CLR};
static volatile uint32_t * const fio_pin[]  = {&FIO0PIN, &FIO1PIN, &FIO2PIN, &FIO3PIN, &FIO4PIN};

int gpio_init(void) {
    // Fast GPIO already enabled in startup.s (SCS bit 0)

    // Configure gate output pin
    gpio_set_output(PIN_GATE_PORT, PIN_GATE_PIN);
    gpio_clear(PIN_GATE_PORT, PIN_GATE_PIN);

    DBG_INFO("GPIO: init complete");
    return 0;
}

void gpio_set_output(uint8_t port, uint8_t pin) {
    if (port > 4 || pin > 31) return;
    *fio_dir[port] |= (1 << pin);
}

void gpio_set_input(uint8_t port, uint8_t pin) {
    if (port > 4 || pin > 31) return;
    *fio_dir[port] &= ~(1 << pin);
}

void gpio_write(uint8_t port, uint8_t pin, bool value) {
    if (value) {
        gpio_set(port, pin);
    } else {
        gpio_clear(port, pin);
    }
}

bool gpio_read(uint8_t port, uint8_t pin) {
    if (port > 4 || pin > 31) return false;
    return (*fio_pin[port] & (1 << pin)) != 0;
}

void gpio_set(uint8_t port, uint8_t pin) {
    if (port > 4 || pin > 31) return;
    *fio_set[port] = (1 << pin);
}

void gpio_clear(uint8_t port, uint8_t pin) {
    if (port > 4 || pin > 31) return;
    *fio_clr[port] = (1 << pin);
}

void gpio_toggle(uint8_t port, uint8_t pin) {
    if (gpio_read(port, pin)) {
        gpio_clear(port, pin);
    } else {
        gpio_set(port, pin);
    }
}
