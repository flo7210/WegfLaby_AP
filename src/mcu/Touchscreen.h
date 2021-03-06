/*
 * Copyright (c) 2006 Jens Rotter, Revision 0.99
 * Copyright (c) 2009 Atmel Corporation. All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Re distributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * 2. Re distributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * 3. The name of Atmel may not be used to endorse or promote products derived
 * from this software without specific prior written permission.
 *
 * 4. This software may only be redistributed and used in connection with an Atmel
 * AVR product.
 *
 * THIS SOFTWARE IS PROVIDED BY ATMEL "AS IS" AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT ARE
 * EXPRESSLY AND SPECIFICALLY DISCLAIMED. IN NO EVENT SHALL ATMEL BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 */

#ifndef TOUCHSCREEN_H
#define TOUCHSCREEN_H

/****************************************************************************
  Libraries
****************************************************************************/

#include <avr/io.h>
#include "uart.h"

/****************************************************************************
  Touchscreen & Measurement Type
****************************************************************************/

// Setting Mode (4wire: (Lowlevel or Rtouch Measurement) || 5wire: (only Lowlevel Measurement available))

//#define FOUR_WIRE
#define LOW_LEVEL_MEASUREMENT
//#define R_TOUCH_MEASUREMENT
#define FIVE_WIRE

/****************************************************************************
  Function definitions
****************************************************************************/

void                  Start_Measurement(void);
void                  Stop_Measurement(void);
void                  Store_valid_Data(void);
void                  ADC_Measurement(void);
void                  Insertion_Sort(short int Array[]);
extern void           Touchscreen_Init(void);

/****************************************************************************
  Global variable
****************************************************************************/

typedef struct {
    unsigned char Flag_Register; 
    short int x_pos;
    short int y_pos;    
} Interface;
extern Interface Touchscreen_Data;

/****************************************************************************
  Global definitions
****************************************************************************/

// Bit Definitions for Interface Touchscreen_Data.Flag_Register
#define FLAG_REGISTER_START                               7
#define FLAG_REGISTER_SLEEP                               6

#define FLAG_REGISTER_TOUCH                               3
#define FLAG_REGISTER_END                                 2
#define FLAG_REGISTER_COORDINATES                         1
#define FLAG_REGISTER_OVERFLOW                            0

// Macros
#define ClearBit(ADRESS,BIT)                              (ADRESS&=~(1<<BIT))
#define SetBit(ADRESS,BIT)                                (ADRESS|=(1<<BIT))
#define TestBit(ADRESS,BIT)                               ((ADRESS&(1<<BIT)))
#define ToogleBit(ADRESS, BIT)                            ((ADRESS) ^= (1 << (BIT))) 

#define Pin_Pullup(Pin)                                   (SetBit(TOUCHSCREEN_OUTPUT, (Pin)), ClearBit(TOUCHSCREEN_DDR, (Pin)))
#define Pin_Vcc(Pin)                                      (SetBit(TOUCHSCREEN_OUTPUT, (Pin)), SetBit(TOUCHSCREEN_DDR, (Pin)))
#define Pin_Gnd(Pin)                                      (ClearBit(TOUCHSCREEN_OUTPUT, (Pin)), SetBit(TOUCHSCREEN_DDR, (Pin)))
#define Pin_Hi_Z(Pin)                                     (ClearBit(TOUCHSCREEN_DDR, (Pin)), ClearBit(TOUCHSCREEN_OUTPUT, (Pin)))

#define Check_Overflow(Flag)                              if(TestBit(Touchscreen_Data.Flag_Register,(Flag))) SetBit(Touchscreen_Data.Flag_Register, FLAG_REGISTER_OVERFLOW)
#define STOP_TOUCHSCREEN                                  (TIMER0_CONTROL_REGISTER_B = (0 << TIMER0_CLOCK_SELECT), ClearBit(PIN_CHANGE_INTERRUPT_CONTROL_REGISTER, PIN_CHANGE_INTERRUPT_ENABLE_1), ADC_CONTROL_AND_STATUS_REGISTER_A  = 0)

// USART Settings
#define USART_BAUD_RATE                                   115200UL
//#define F_CPU                                             16000000UL
#define MY_UBRR                                           F_CPU/16/USART_BAUD_RATE-1

// Timer0 Settings (1ms Interval)
#define TIMER0_INITIAL_VALUE_COMPARE_MATCH_A              124
#define TIMER0_INITIAL_VALUE_COMPARE_MATCH_B              80
#define TIMER0_PRESCALER                                  3             // :64
#define DEBOUNCE_TIME                                     8             // 8 * 1ms
#define SLEEP_COUNTDOWN                                   2000          // 2000 * 1ms ... SLEEP_COUNTDOWN !> DEBOUNCE TIME

// ADC Settings
#define ADC_PRESCALER                                     7             // :64 --> 125kHz
#define START_CONVERSION                                  (SetBit(ADC_CONTROL_AND_STATUS_REGISTER_A, ADC_START_CONVERSION))

// Measurement Settings
#define SAMPLES_FOR_ONE_TRUE_XY_PAIR                      9             // Number of Measurements for one true X/Y-Coordinate
#define END_OF_ARRAY                                      SAMPLES_FOR_ONE_TRUE_XY_PAIR-1
#define MEDIAN                                            (SAMPLES_FOR_ONE_TRUE_XY_PAIR+1)/2      // odd-numbered: SAMPLES_FOR_ONE_TRUE_XY_PAIR
#define MAXIMUM_LOW_LEVEL                                 300           // Invalid Measurement for Low_Level > MAXIMUM_LOW_LEVEL
#define MAXIMUM_RTOUCH_LEVEL                              2000          // Invalid Measurement for R_Touch   > MAXIMUM_RTOUCH_LEVEL
#define MAXIMUM_UNTOUCH_CONDITIONS                        10            // Number of (successive) Invalid Measurements till Untouch Condition (10 * 1ms)

/****************************************************************************
  Device dependent defines
****************************************************************************/



/****************************************************************************
  4-wire
****************************************************************************/
#if defined FOUR_WIRE

// Register Definitions

// I/O
#define TOUCHSCREEN_INPUT                                 PINC
#define TOUCHSCREEN_OUTPUT                                PORTC
#define TOUCHSCREEN_DDR                                   DDRC
// Pin Change
#define PIN_CHANGE_INTERRUPT_CONTROL_REGISTER             PCICR
#define PIN_CHANGE_INTERRUPT_FLAG_REGISTER                PCIFR
#define PIN_CHANGE_MASK_1_REGISTER                        PCMSK1

// Bit Definitions

// I/O - 4wire
#define XP		                                  0             // Left Side
#define XN		                                  1             // Right Side
#define YP		                                  2             // Upper Side
#define YN		                                  3             // Lower Side
#define ADC1                                              XN            // Y-Coordinate Reading & Z1 Reading
#define ADC2                                              YP            // Z2 Reading
#define STANDBY_PIN                                       YN            // Pin Change & Low_Level_Readings & X-Coordinate Reading

// Pin Change
#define PIN_CHANGE_INTERRUPT_ENABLE_1                     PCIE1
#define PIN_CHANGE_INTERRUPT_FLAG_1                       PCIF1
#define PIN_CHANGE_ENABLE_MASK                            PCINT11

// I/O States
#define STANDBY_CONFIGURATION                             (Pin_Gnd(XP), Pin_Hi_Z(XN), Pin_Hi_Z(YP), Pin_Pullup(YN))
#define X_POS_CONFIGURATION                               (Pin_Gnd(XP), Pin_Vcc(XN), Pin_Hi_Z(YP), Pin_Hi_Z(YN))
#define Y_POS_CONFIGURATION                               (Pin_Hi_Z(XP), Pin_Hi_Z(XN), Pin_Gnd(YP), Pin_Vcc(YN))
#define HI_Z_CONFIGURATION                                (Pin_Hi_Z(XP), Pin_Hi_Z(XN), Pin_Hi_Z(YP), Pin_Hi_Z(YN))
#define Z_1_AND_2_CONFIGURATION                           (Pin_Gnd(XP), Pin_Hi_Z(XN), Pin_Hi_Z(YP), Pin_Vcc(YN))

#endif

/****************************************************************************
  5-wire
****************************************************************************/
#if defined FIVE_WIRE

// Register Definitions

// I/O
#define TOUCHSCREEN_INPUT                                 PINC
#define TOUCHSCREEN_OUTPUT                                PORTC
#define TOUCHSCREEN_DDR                                   DDRC
// Pin Change
#define PIN_CHANGE_INTERRUPT_CONTROL_REGISTER             PCICR
#define PIN_CHANGE_INTERRUPT_FLAG_REGISTER                PCIFR
#define PIN_CHANGE_MASK_1_REGISTER                        PCMSK1

// Bit Definitions

// I/O - 5wire
#define UL		                                  1             // Upper Left Corner
#define UR		                                  4             // Upper Right Corner
#define LL		                                  0             // Lower Left Corner
#define LR		                                  3             // Lower Right Corner
#define STANDBY_PIN                                       2             // Pin Change & All ADC Readings
#define ADC1                                              STANDBY_PIN

// Pin Change
#define PIN_CHANGE_INTERRUPT_ENABLE_1                     PCIE1
#define PIN_CHANGE_INTERRUPT_FLAG_1                       PCIF1
#define PIN_CHANGE_ENABLE_MASK                            PCINT12

// I/O States
#define STANDBY_CONFIGURATION                             (Pin_Gnd(UL), Pin_Hi_Z(UR), Pin_Hi_Z(LL), Pin_Hi_Z(LR), Pin_Pullup(STANDBY_PIN))
#define X_POS_CONFIGURATION                               (Pin_Gnd(UL), Pin_Vcc(UR), Pin_Gnd(LL), Pin_Vcc(LR), Pin_Hi_Z(STANDBY_PIN))
#define Y_POS_CONFIGURATION                               (Pin_Gnd(UL), Pin_Gnd(UR), Pin_Vcc(LL), Pin_Vcc(LR), Pin_Hi_Z(STANDBY_PIN))
#define HI_Z_CONFIGURATION                                (Pin_Hi_Z(UL), Pin_Hi_Z(UR), Pin_Hi_Z(LL), Pin_Hi_Z(LR), Pin_Hi_Z(STANDBY_PIN))

#endif

/****************************************************************************
  General Device dependent defines
****************************************************************************/

// Interrupt Vector Definitions
#define PIN_CHANGE_VECTOR                                 PCINT1_vect
#define TIMER0_COMPARE_MATCH_A_VECTOR                     TIMER0_COMPA_vect
#define TIMER0_COMPARE_MATCH_B_VECTOR                     TIMER0_COMPB_vect
#define ADC_CONVERSION_COMPLETE_VECTOR                    ADC_vect

// Register Definitions
// Timer0
#define TIMER0_INTERRUPT_MASK_REGISTER                    TIMSK0
#define TIMER0_INTERRUPT_FLAG_REGISTER                    TIFR0
#define TIMER0_OUTPUT_COMPARE_REGISTER_A                  OCR0A
#define TIMER0_OUTPUT_COMPARE_REGISTER_B                  OCR0B
#define TIMER0_CONTROL_REGISTER_A                         TCCR0A
#define TIMER0_CONTROL_REGISTER_B                         TCCR0B

// ADC
#define ADC_CONTROL_AND_STATUS_REGISTER_A                 ADCSRA
#define ADC_MULTIPLEXER_SELECTION_REGISTER                ADMUX  

// Bit Definitions
// Timer0
#define TIMER0_CLOCK_SELECT                               CS00
#define TIMER0_OUTPUT_COMPARE_A_INT_ENABLE                OCIE0A
#define TIMER0_OUTPUT_COMPARE_B_INT_ENABLE                OCIE0B
#define TIMER0_OUTPUT_COMPARE_B_MATCH_FLAG                OCF0B
#define TIMER0_WAVEFORM_GENERATION_MODE                   WGM00

// ADC
#define ADC_ENABLE                                        ADEN
#define ADC_START_CONVERSION                              ADSC
#define ADC_INTERRUPT_ENABLE                              ADIE
#define ADC_PRESCALER_SELECT                              ADPS0
#define ADC_REFERENCE_SELECTION                           REFS0

#endif // TOUCHSCREEN_H 
