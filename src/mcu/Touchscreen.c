/*
 * vim:ts=4:sw=4:expandtab
 *
 * Copyright (c) 2006 Jens Rotter, Revision 0.99
 * Copyright (c) 2010 Michael Stapelberg, Peter Treiber
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


/****************************************************************************
  Libraries
****************************************************************************/

#include <avr/io.h>
#include <stdio.h>
#include <avr/interrupt.h>
#include "Touchscreen.h"

enum {
    STATE_READ_X = 0,
    STATE_READ_Y = 1,
    STATE_VERIFY_TOUCH = 2
} current_state = STATE_READ_X;

/****************************************************************************
  Global variable
****************************************************************************/

// Interface variable
Interface Touchscreen_Data;

// Manages Measurements
volatile unsigned char ADC_ISR_Switch=1;

// Array for X/Y-Coordinates
static short int Readings_X_Pos[SAMPLES_FOR_ONE_TRUE_XY_PAIR];
static short int Readings_Y_Pos[SAMPLES_FOR_ONE_TRUE_XY_PAIR]; 
static unsigned char i_array;

/****************************************************************************
  Interrupts
****************************************************************************/

/*
 * Dieser Interrupt wird zuerst ausgeführt. Hier wird die Spannung angelegt
 * um jeweils die X- oder Y-Koordinate zu messen.
 *
 */
ISR(TIMER0_COMPARE_MATCH_B_VECTOR) {
    switch (current_state) {
    case STATE_READ_X:
        Pin_Gnd(UL);
        Pin_Vcc(UR);
        Pin_Gnd(LL);
        Pin_Vcc(LR);
        Pin_Hi_Z(STANDBY_PIN);
        break;

    case STATE_READ_Y:
        Pin_Gnd(UL);
        Pin_Gnd(UR);
        Pin_Vcc(LL);
        Pin_Vcc(LR);
        Pin_Hi_Z(STANDBY_PIN);
        break;

    case STATE_VERIFY_TOUCH:
        Pin_Gnd(UL);
        Pin_Hi_Z(UR);
        Pin_Hi_Z(LL);
        Pin_Hi_Z(LR);
        Pin_Pullup(STANDBY_PIN);
        break;
    }
}

/*
 * Dieser Interrupt wird als zweites ausgeführt. Er startet die
 * Analog/Digital-Wandlung.
 *
 */
ISR(TIMER0_COMPARE_MATCH_A_VECTOR) {
    START_CONVERSION;
}

/*
 * Sobald die Wandlung vollständig ist, wird dieser Interrupt aufgerufen.
 *
 */
ISR(ADC_CONVERSION_COMPLETE_VECTOR) {
    switch (current_state) {
    case STATE_READ_X:
        Readings_X_Pos[i_array] = ADC;
        break;

    case STATE_READ_Y:
        Readings_Y_Pos[i_array] = ADC;
        break;

    case STATE_VERIFY_TOUCH:
        /* Wenn kein Druck mehr festgestellt wurde, werden die Koordinaten
         * nicht gespeichert. */
        if (ADC >= MAXIMUM_LOW_LEVEL)
            return;

        /* Valide Koordinaten verfügbar: */
        Store_valid_Data();
        break;
    }

    current_state = (current_state + 1) % 3;
}

/****************************************************************************
  Function declarations
****************************************************************************/
void Touchscreen_Init(void) {
    // Timer0 Initialization (CTC Mode)
    // Set Clear Timer on Compare Match A
    TIMER0_CONTROL_REGISTER_A = (2 << TIMER0_WAVEFORM_GENERATION_MODE);
    /* Zunächst Interrupt B ausführen lassen */
    OCR0B = 80;
    /* danach Interrupt A */
    OCR0A = 124;
    /* Interrupts aktivieren für beide Timer */
    TIMSK0 = (1 << OCIE0A) | (1 << OCIE0B);

    /* Prescaler wird auf clk_IO/64 gesetzt */
    TCCR0B = (3 << CS00);

    /* ADC aktivieren, Interrupts aktivieren, Prescaler auf clk_IO/128 setzen */
    ADCSRA = (1 << ADC_ENABLE) |
             (1 << ADC_INTERRUPT_ENABLE) |
             (7 << ADPS0);

    /* Bei einem 5-wire-Touchscreen wird am Standby-Pin gemessen */
    ADMUX = STANDBY_PIN | (1 << REFS0);
}

void Insertion_Sort(short int Array[])
{
	signed char i;
	unsigned char j;
        short int current;
	
        // Sort Array[]
        for(j=1; j<SAMPLES_FOR_ONE_TRUE_XY_PAIR; j++) 
        {
              current = Array[j]; 
              i = j - 1;
              while(i>=0 && Array[i]>current) 
              {
                    Array[i+1] = Array[i];
                    i--;
              }
              Array[i+1] = current;
	}
}

void Store_valid_Data(void)
{
    if (i_array < END_OF_ARRAY) {
        i_array++;
        return;
    }

    // Sort X/Y Readings To Get Median
    Insertion_Sort(Readings_X_Pos);
    Insertion_Sort(Readings_Y_Pos);

    // Interface: Check If Old Coordinates Were Read, Otherwise Set Overflow Flag
    Check_Overflow(FLAG_REGISTER_COORDINATES);

    // Interface: Make New Coordinates Available
    Touchscreen_Data.x_pos = Readings_X_Pos[MEDIAN];
    Touchscreen_Data.y_pos = Readings_Y_Pos[MEDIAN];

    // Interface: New Event --> New Coordinates Ready
    SetBit(Touchscreen_Data.Flag_Register, FLAG_REGISTER_COORDINATES);

    // Reset i_array
    i_array=0;
}
