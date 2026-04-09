#ifndef GPIO_H
#define GPIO_H

#include <stdint.h>
#include <stdbool.h>

int gpio_init(void);

void gpio_set_output(uint8_t port, uint8_t pin);
void gpio_set_input(uint8_t port, uint8_t pin);

void gpio_write(uint8_t port, uint8_t pin, bool value);
bool gpio_read(uint8_t port, uint8_t pin);

void gpio_set(uint8_t port, uint8_t pin);
void gpio_clear(uint8_t port, uint8_t pin);
void gpio_toggle(uint8_t port, uint8_t pin);

#endif // GPIO_H
