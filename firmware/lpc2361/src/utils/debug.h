#ifndef DEBUG_H
#define DEBUG_H

#include <stdio.h>
#include "config.h"

/*
 * Debug levels:
 * 0 = Off (production build)
 * 1 = Errors only
 * 2 = Errors + Info
 * 3 = Errors + Info + Verbose (spammy)
 */

#ifndef DEBUG_LEVEL
#define DEBUG_LEVEL 2
#endif

// Error: Always important, something went wrong
#if DEBUG_LEVEL >= 1
  #define DBG_ERR(fmt, ...) printf("[ERR %s:%d] " fmt "\r\n", __FILE__, __LINE__, ##__VA_ARGS__)
#else
  #define DBG_ERR(fmt, ...)
#endif

// Info: State changes, init steps, useful events
#if DEBUG_LEVEL >= 2
  #define DBG_INFO(fmt, ...) printf("[INF] " fmt "\r\n", ##__VA_ARGS__)
#else
  #define DBG_INFO(fmt, ...)
#endif

// Verbose: Every tick, every byte, very spammy
#if DEBUG_LEVEL >= 3
  #define DBG_VERB(fmt, ...) printf("[VRB] " fmt "\r\n", ##__VA_ARGS__)
#else
  #define DBG_VERB(fmt, ...)
#endif

// Assert with message
#define DBG_ASSERT(cond, fmt, ...) \
    do { \
        if (!(cond)) { \
            DBG_ERR("ASSERT FAIL: " fmt, ##__VA_ARGS__); \
            while(1); \
        } \
    } while(0)

// Print hex dump (for MIDI debugging)
#if DEBUG_LEVEL >= 3
static inline void dbg_hexdump(const char* label, const uint8_t* data, int len) {
    printf("[HEX] %s: ", label);
    for (int i = 0; i < len; i++) {
        printf("%02X ", data[i]);
    }
    printf("\r\n");
}
#else
#define dbg_hexdump(label, data, len)
#endif

#endif // DEBUG_H
