#ifndef LPC2361_H
#define LPC2361_H

/*
 * LPC2361 Register Definitions
 * NXP ARM7TDMI-S, 128KB Flash, 34KB SRAM
 *
 * Memory map:
 *   0x0000_0000 - 0x0001_FFFF : Flash (128KB)
 *   0x4000_0000 - 0x4000_87FF : SRAM (34KB)
 *   0xE000_0000 - 0xE01F_FFFF : APB peripherals
 *   0xFFE0_0000 - 0xFFFF_FFFF : AHB peripherals + VIC
 *   0xFFFF_F000 - 0xFFFF_FFFF : Boot ROM
 */

#include <stdint.h>

#define __IO volatile
#define __I  volatile const

/* ============================================================
 * System Control Block
 * ============================================================ */

// Memory Accelerator Module (MAM)
#define MAMCR    (*((__IO uint32_t *)0xE01FC000))
#define MAMTIM   (*((__IO uint32_t *)0xE01FC004))

// PLL0 (Main PLL)
#define PLL0CON  (*((__IO uint32_t *)0xE01FC080))
#define PLL0CFG  (*((__IO uint32_t *)0xE01FC084))
#define PLL0STAT (*((__I  uint32_t *)0xE01FC088))
#define PLL0FEED (*((__IO uint32_t *)0xE01FC08C))

// Clock divider
#define CCLKCFG  (*((__IO uint32_t *)0xE01FC104))

// Power control
#define PCON     (*((__IO uint32_t *)0xE01FC0C0))
#define PCONP    (*((__IO uint32_t *)0xE01FC0C4))

// Clock source select
#define CLKSRCSEL (*((__IO uint32_t *)0xE01FC10C))

// Peripheral clock select
#define PCLKSEL0 (*((__IO uint32_t *)0xE01FC1A8))
#define PCLKSEL1 (*((__IO uint32_t *)0xE01FC1AC))

// External interrupts
#define EXTINT   (*((__IO uint32_t *)0xE01FC140))
#define EXTMODE  (*((__IO uint32_t *)0xE01FC148))
#define EXTPOLAR (*((__IO uint32_t *)0xE01FC14C))

// System control miscellaneous
#define SCS      (*((__IO uint32_t *)0xE01FC1A0))

/* ============================================================
 * Pin Connect Block
 * ============================================================ */

#define PINSEL0  (*((__IO uint32_t *)0xE002C000))
#define PINSEL1  (*((__IO uint32_t *)0xE002C004))
#define PINSEL2  (*((__IO uint32_t *)0xE002C008))
#define PINSEL3  (*((__IO uint32_t *)0xE002C00C))
#define PINSEL4  (*((__IO uint32_t *)0xE002C010))
#define PINSEL5  (*((__IO uint32_t *)0xE002C014))
#define PINSEL6  (*((__IO uint32_t *)0xE002C018))
#define PINSEL7  (*((__IO uint32_t *)0xE002C01C))
#define PINSEL8  (*((__IO uint32_t *)0xE002C020))
#define PINSEL9  (*((__IO uint32_t *)0xE002C024))
#define PINSEL10 (*((__IO uint32_t *)0xE002C028))

// Pin mode (pull-up/pull-down/none)
#define PINMODE0 (*((__IO uint32_t *)0xE002C040))
#define PINMODE1 (*((__IO uint32_t *)0xE002C044))
#define PINMODE2 (*((__IO uint32_t *)0xE002C048))
#define PINMODE3 (*((__IO uint32_t *)0xE002C04C))
#define PINMODE4 (*((__IO uint32_t *)0xE002C050))

/* ============================================================
 * Fast GPIO (active on ports 0 and 1)
 * ============================================================ */

// Port 0
#define FIO0DIR  (*((__IO uint32_t *)0x3FFFC000))
#define FIO0MASK (*((__IO uint32_t *)0x3FFFC010))
#define FIO0PIN  (*((__IO uint32_t *)0x3FFFC014))
#define FIO0SET  (*((__IO uint32_t *)0x3FFFC018))
#define FIO0CLR  (*((__IO uint32_t *)0x3FFFC01C))

// Port 1
#define FIO1DIR  (*((__IO uint32_t *)0x3FFFC020))
#define FIO1MASK (*((__IO uint32_t *)0x3FFFC030))
#define FIO1PIN  (*((__IO uint32_t *)0x3FFFC034))
#define FIO1SET  (*((__IO uint32_t *)0x3FFFC038))
#define FIO1CLR  (*((__IO uint32_t *)0x3FFFC03C))

// Port 2
#define FIO2DIR  (*((__IO uint32_t *)0x3FFFC040))
#define FIO2MASK (*((__IO uint32_t *)0x3FFFC050))
#define FIO2PIN  (*((__IO uint32_t *)0x3FFFC054))
#define FIO2SET  (*((__IO uint32_t *)0x3FFFC058))
#define FIO2CLR  (*((__IO uint32_t *)0x3FFFC05C))

// Port 3
#define FIO3DIR  (*((__IO uint32_t *)0x3FFFC060))
#define FIO3MASK (*((__IO uint32_t *)0x3FFFC070))
#define FIO3PIN  (*((__IO uint32_t *)0x3FFFC074))
#define FIO3SET  (*((__IO uint32_t *)0x3FFFC078))
#define FIO3CLR  (*((__IO uint32_t *)0x3FFFC07C))

// Port 4
#define FIO4DIR  (*((__IO uint32_t *)0x3FFFC080))
#define FIO4MASK (*((__IO uint32_t *)0x3FFFC090))
#define FIO4PIN  (*((__IO uint32_t *)0x3FFFC094))
#define FIO4SET  (*((__IO uint32_t *)0x3FFFC098))
#define FIO4CLR  (*((__IO uint32_t *)0x3FFFC09C))

/* ============================================================
 * UART0
 * ============================================================ */

#define U0RBR   (*((__I  uint32_t *)0xE000C000))  // Receive buffer (DLAB=0)
#define U0THR   (*((__IO uint32_t *)0xE000C000))  // Transmit hold (DLAB=0)
#define U0DLL   (*((__IO uint32_t *)0xE000C000))  // Divisor latch LSB (DLAB=1)
#define U0DLM   (*((__IO uint32_t *)0xE000C004))  // Divisor latch MSB (DLAB=1)
#define U0IER   (*((__IO uint32_t *)0xE000C004))  // Interrupt enable (DLAB=0)
#define U0IIR   (*((__I  uint32_t *)0xE000C008))  // Interrupt ID
#define U0FCR   (*((__IO uint32_t *)0xE000C008))  // FIFO control
#define U0LCR   (*((__IO uint32_t *)0xE000C00C))  // Line control
#define U0LSR   (*((__I  uint32_t *)0xE000C014))  // Line status
#define U0SCR   (*((__IO uint32_t *)0xE000C01C))  // Scratch
#define U0TER   (*((__IO uint32_t *)0xE000C030))  // Transmit enable

// UART0 LSR bits
#define U0LSR_RDR   (1 << 0)  // Receiver data ready
#define U0LSR_THRE  (1 << 5)  // Transmit holding register empty
#define U0LSR_TEMT  (1 << 6)  // Transmitter empty

/* ============================================================
 * UART1
 * ============================================================ */

#define U1RBR   (*((__I  uint32_t *)0xE0010000))
#define U1THR   (*((__IO uint32_t *)0xE0010000))
#define U1DLL   (*((__IO uint32_t *)0xE0010000))
#define U1DLM   (*((__IO uint32_t *)0xE0010004))
#define U1IER   (*((__IO uint32_t *)0xE0010004))
#define U1IIR   (*((__I  uint32_t *)0xE0010008))
#define U1FCR   (*((__IO uint32_t *)0xE0010008))
#define U1LCR   (*((__IO uint32_t *)0xE001000C))
#define U1LSR   (*((__I  uint32_t *)0xE0010014))

/* ============================================================
 * Timer 0
 * ============================================================ */

#define T0IR    (*((__IO uint32_t *)0xE0004000))  // Interrupt register
#define T0TCR   (*((__IO uint32_t *)0xE0004004))  // Timer control
#define T0TC    (*((__IO uint32_t *)0xE0004008))  // Timer counter
#define T0PR    (*((__IO uint32_t *)0xE000400C))  // Prescale register
#define T0PC    (*((__IO uint32_t *)0xE0004010))  // Prescale counter
#define T0MCR   (*((__IO uint32_t *)0xE0004014))  // Match control
#define T0MR0   (*((__IO uint32_t *)0xE0004018))  // Match 0
#define T0MR1   (*((__IO uint32_t *)0xE000401C))  // Match 1
#define T0MR2   (*((__IO uint32_t *)0xE0004020))  // Match 2
#define T0MR3   (*((__IO uint32_t *)0xE0004024))  // Match 3

/* ============================================================
 * Timer 1
 * ============================================================ */

#define T1IR    (*((__IO uint32_t *)0xE0008000))
#define T1TCR   (*((__IO uint32_t *)0xE0008004))
#define T1TC    (*((__IO uint32_t *)0xE0008008))
#define T1PR    (*((__IO uint32_t *)0xE000800C))
#define T1MCR   (*((__IO uint32_t *)0xE0008014))
#define T1MR0   (*((__IO uint32_t *)0xE0008018))

/* ============================================================
 * DAC (10-bit)
 * ============================================================ */

#define DACR    (*((__IO uint32_t *)0xE006C000))
// DACR bits: [15:6] = VALUE (10 bits), [16] = BIAS

/* ============================================================
 * ADC
 * ============================================================ */

#define AD0CR   (*((__IO uint32_t *)0xE0034000))  // Control
#define AD0GDR  (*((__I  uint32_t *)0xE0034004))  // Global data
#define AD0STAT (*((__I  uint32_t *)0xE0034030))  // Status
#define AD0DR0  (*((__I  uint32_t *)0xE0034010))  // Channel 0
#define AD0DR1  (*((__I  uint32_t *)0xE0034014))
#define AD0DR2  (*((__I  uint32_t *)0xE0034018))
#define AD0DR3  (*((__I  uint32_t *)0xE003401C))
#define AD0DR4  (*((__I  uint32_t *)0xE0034020))
#define AD0DR5  (*((__I  uint32_t *)0xE0034024))
#define AD0DR6  (*((__I  uint32_t *)0xE0034028))
#define AD0DR7  (*((__I  uint32_t *)0xE003402C))

/* ============================================================
 * I2C0
 * ============================================================ */

#define I2C0CONSET  (*((__IO uint32_t *)0xE001C000))
#define I2C0STAT    (*((__I  uint32_t *)0xE001C004))
#define I2C0DAT     (*((__IO uint32_t *)0xE001C008))
#define I2C0ADR     (*((__IO uint32_t *)0xE001C00C))
#define I2C0SCLH    (*((__IO uint32_t *)0xE001C010))
#define I2C0SCLL    (*((__IO uint32_t *)0xE001C014))
#define I2C0CONCLR  (*((__IO uint32_t *)0xE001C018))

// I2C CONSET bits
#define I2C_AA   (1 << 2)
#define I2C_SI   (1 << 3)
#define I2C_STO  (1 << 4)
#define I2C_STA  (1 << 5)
#define I2C_EN   (1 << 6)

/* ============================================================
 * SPI (SSP0)
 * ============================================================ */

#define SSP0CR0  (*((__IO uint32_t *)0xE0068000))
#define SSP0CR1  (*((__IO uint32_t *)0xE0068004))
#define SSP0DR   (*((__IO uint32_t *)0xE0068008))
#define SSP0SR   (*((__I  uint32_t *)0xE006800C))
#define SSP0CPSR (*((__IO uint32_t *)0xE0068010))

/* ============================================================
 * Vectored Interrupt Controller (VIC)
 * ============================================================ */

#define VICIRQStatus    (*((__I  uint32_t *)0xFFFFF000))
#define VICFIQStatus    (*((__I  uint32_t *)0xFFFFF004))
#define VICRawIntr      (*((__I  uint32_t *)0xFFFFF008))
#define VICIntSelect    (*((__IO uint32_t *)0xFFFFF00C))
#define VICIntEnable    (*((__IO uint32_t *)0xFFFFF010))
#define VICIntEnClr     (*((__IO uint32_t *)0xFFFFF014))
#define VICSoftInt      (*((__IO uint32_t *)0xFFFFF018))
#define VICSoftIntClr   (*((__IO uint32_t *)0xFFFFF01C))
#define VICProtection   (*((__IO uint32_t *)0xFFFFF020))
#define VICVectAddr     (*((__IO uint32_t *)0xFFFFF030))
#define VICDefVectAddr  (*((__IO uint32_t *)0xFFFFF034))

// VIC vector address registers (32 slots)
#define VICVectAddr0    (*((__IO uint32_t *)0xFFFFF100))
#define VICVectAddr1    (*((__IO uint32_t *)0xFFFFF104))
#define VICVectAddr2    (*((__IO uint32_t *)0xFFFFF108))
#define VICVectAddr3    (*((__IO uint32_t *)0xFFFFF10C))

// VIC priority registers
#define VICVectPriority0 (*((__IO uint32_t *)0xFFFFF200))
#define VICVectPriority1 (*((__IO uint32_t *)0xFFFFF204))

// VIC interrupt sources (LPC2361)
#define VIC_WDT      0
#define VIC_TIMER0   4
#define VIC_TIMER1   5
#define VIC_UART0    6
#define VIC_UART1    7
#define VIC_I2C0     9
#define VIC_SPI      10
#define VIC_SSP0     10
#define VIC_SSP1     11
#define VIC_PLL      12
#define VIC_RTC      13
#define VIC_EINT0    14
#define VIC_EINT1    15
#define VIC_EINT2    16
#define VIC_EINT3    17
#define VIC_ADC0     18
#define VIC_I2C1     19
#define VIC_BOD      20
#define VIC_ADC1     21
#define VIC_USB      22

/* ============================================================
 * Code Read Protection (CRP)
 * ============================================================ */

// CRP word at address 0x000001FC
#define CRP_NONE   0xFFFFFFFF  // No protection
#define CRP_CRP1   0x12345678  // Partial protection (ISP read disabled)
#define CRP_CRP2   0x87654321  // More protection (ISP write disabled)
#define CRP_CRP3   0x43218765  // Full protection (no ISP, no JTAG)
// WARNING: CRP3 makes the chip unrecoverable without full erase

#endif // LPC2361_H
