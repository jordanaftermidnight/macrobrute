/*
 * Newlib syscall stubs
 * Redirects printf to UART0 for debug output
 */

#include <sys/stat.h>
#include <errno.h>
#include "drivers/uart.h"

// _write - called by printf
int _write(int fd, char *buf, int len) {
    (void)fd;
    for (int i = 0; i < len; i++) {
        uart_putc(0, buf[i]);  // UART0 = debug
    }
    return len;
}

// _read - not implemented
int _read(int fd, char *buf, int len) {
    (void)fd; (void)buf; (void)len;
    return -1;
}

// Required stubs
int _close(int fd) { (void)fd; return -1; }
int _lseek(int fd, int offset, int whence) { (void)fd; (void)offset; (void)whence; return -1; }
int _fstat(int fd, struct stat *st) { (void)fd; st->st_mode = S_IFCHR; return 0; }
int _isatty(int fd) { (void)fd; return 1; }

// Memory allocation
extern char _end;
static char *heap_end = NULL;

void *_sbrk(int incr) {
    char *prev_heap_end;

    if (heap_end == NULL) {
        heap_end = &_end;
    }
    prev_heap_end = heap_end;
    heap_end += incr;

    return prev_heap_end;
}
