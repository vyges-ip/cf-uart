/*
	Copyright 2025 ChipFoundry, a DBA of Umbralogic Technologies LLC
	Copyright 2025 Efabless Corp.


	Licensed under the Apache License, Version 2.0 (the "License");
	you may not use this file except in compliance with the License.
	You may obtain a copy of the License at

	    www.apache.org/licenses/LICENSE-2.0

	Unless required by applicable law or agreed to in writing, software
	distributed under the License is distributed on an "AS IS" BASIS,
	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	See the License for the specific language governing permissions and
	limitations under the License.

*/


/*! \file CF_UART.c
    \brief C file for UART APIs which contains the function implmentations 
    
*/

#ifndef CF_UART_C
#define CF_UART_C

/******************************************************************************
* Includes
******************************************************************************/
#include "CF_UART.h"

/******************************************************************************
* File-Specific Macros and Constants
******************************************************************************/



/******************************************************************************
* Static Variables
******************************************************************************/



/******************************************************************************
* Static Function Prototypes
******************************************************************************/



/******************************************************************************
* Function Definitions
******************************************************************************/

CF_DRIVER_STATUS CF_UART_setGclkEnable(CF_UART_TYPE_PTR uart, uint32_t value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK;

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;    // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if ((value < (uint32_t)0x0) || (value > (uint32_t)0x1)) {  
        status = CF_DRIVER_ERROR_PARAMETER;    // Return CF_DRIVER_ERROR_PARAMETER if value is out of range
    }else {
        uart->GCLK = value;                     // Set the GCLK enable bit to the given value
    }

    return status;
}

CF_DRIVER_STATUS CF_UART_enable(CF_UART_TYPE_PTR uart){

    CF_DRIVER_STATUS status = CF_DRIVER_OK;

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL |= CF_UART_CTRL_REG_EN_MASK;   // set the enable bit to 1 at the specified offset
        
    }   

    return status;
}

CF_DRIVER_STATUS CF_UART_disable(CF_UART_TYPE_PTR uart){

    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL &= ~(CF_UART_CTRL_REG_EN_MASK);        // Clear the enable bit using the specified  mask
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_enableRx(CF_UART_TYPE_PTR uart){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL |= CF_UART_CTRL_REG_RXEN_MASK; // set the enable bit to 1 at the specified offset
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_disableRx(CF_UART_TYPE_PTR uart){

    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL &= ~(CF_UART_CTRL_REG_RXEN_MASK);      // Clear the enable bit using the specified  mask
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_enableTx(CF_UART_TYPE_PTR uart){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL |= CF_UART_CTRL_REG_TXEN_MASK; // set the enable bit to 1 at the specified offset
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_disableTx(CF_UART_TYPE_PTR uart){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL &= ~(CF_UART_CTRL_REG_TXEN_MASK);      // Clear the enable bit using the specified  mask
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_enableLoopBack(CF_UART_TYPE_PTR uart){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL |= CF_UART_CTRL_REG_LPEN_MASK; // set the enable bit to 1 at the specified offset
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_disableLoopBack(CF_UART_TYPE_PTR uart){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL &= ~(CF_UART_CTRL_REG_LPEN_MASK);      // Clear the enable bit using the specified  mask
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_enableGlitchFilter(CF_UART_TYPE_PTR uart){

    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                 // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL &= ~(CF_UART_CTRL_REG_GFEN_MASK);          // Clear the enable bit using the specified  mask
        uart->CTRL |= CF_UART_CTRL_REG_GFEN_MASK; // set the enable bit to 1 at the specified offset
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_disableGlitchFilter(CF_UART_TYPE_PTR uart){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                 // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else{
        uart->CTRL &= ~(CF_UART_CTRL_REG_GFEN_MASK);          // Clear the enable bit using the specified  mask
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_setCTRL(CF_UART_TYPE_PTR uart, uint32_t value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (value > CF_UART_CTRL_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if value is out of range
    } else {
        uart->CTRL = value;
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_getCTRL(CF_UART_TYPE_PTR uart, uint32_t* CTRL_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (CTRL_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if CTRL_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *CTRL_value = uart->CTRL;
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_setPrescaler(CF_UART_TYPE_PTR uart, uint32_t prescaler){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (prescaler > CF_UART_PR_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if prescaler is out of range
    } else {
        uart->PR = prescaler;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getPrescaler(CF_UART_TYPE_PTR uart, uint32_t* Prescaler_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;             // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (Prescaler_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;             // Return CF_DRIVER_ERROR_PARAMETER if Prescaler_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *Prescaler_value = uart->PR;
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_setDataSize(CF_UART_TYPE_PTR uart, uint32_t value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if ((value < CF_UART_DataLength_MIN_VALUE) || (value > CF_UART_DataLength_MAX_VALUE)) {
        status = CF_DRIVER_ERROR_UNSUPPORTED;              // Return CF_DRIVER_ERROR_UNSUPPORTED if data length is out of range
                                                        // This UART IP only supports data length from 5 to 9 bits
    } else {

        uart->CFG &= ~(CF_UART_CFG_REG_WLEN_MASK);        // Clear the field bits in the register using the defined mask
        uart->CFG |= ((value << CF_UART_CFG_REG_WLEN_BIT) & CF_UART_CFG_REG_WLEN_MASK);     // Set the bits with the given value at the defined offset
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_setStopBits(CF_UART_TYPE_PTR uart, bool is_two_bits){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else {
        if (is_two_bits){
            uart->CFG |= CF_UART_CFG_REG_STP2_MASK; // set the enable bit to 1 at the specified offset
        } else {
            uart->CFG &= ~(CF_UART_CFG_REG_STP2_MASK);      // Clear the enable bit using the specified  mask
        }
        
    }
    return status;
}

// enum parity_type {NONE = 0, ODD = 1, EVEN = 2, STICKY_0 = 4, STICKY_1 = 5};
// This violates misrac 10.1 because the enum is not an essential type, and should not be used as an operand of a logical operator
CF_DRIVER_STATUS CF_UART_setParityType(CF_UART_TYPE_PTR uart, enum parity_type parity){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else {
        uart->CFG &= ~(CF_UART_CFG_REG_PARITY_MASK);      // Clear the field bits in the register using the defined mask
        uart->CFG |= ((parity << CF_UART_CFG_REG_PARITY_BIT) & CF_UART_CFG_REG_PARITY_MASK); // Set the bits with the given value at the defined offset
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_setTimeoutBits(CF_UART_TYPE_PTR uart, uint32_t value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (value > CF_UART_CFG_REG_TIMEOUT_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if value is out of range
    } else {
        uart->CFG &= ~(CF_UART_CFG_REG_TIMEOUT_MASK);            // Clear the field bits in the register using the defined mask
        uart->CFG |= ((value << CF_UART_CFG_REG_TIMEOUT_BIT) & CF_UART_CFG_REG_TIMEOUT_MASK);   // Set the bits with the given value at the defined offset
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_setConfig(CF_UART_TYPE_PTR uart, uint32_t value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (value > CF_UART_CFG_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if value is out of range
    } else {
        uart->CFG = value;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getConfig(CF_UART_TYPE_PTR uart, uint32_t* CFG_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (CFG_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if CFG_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *CFG_value = uart->CFG;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_setRxFIFOThreshold(CF_UART_TYPE_PTR uart, uint32_t value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (value > CF_UART_RX_FIFO_THRESHOLD_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if value is out of range
    } else {
        uart->RX_FIFO_THRESHOLD = value;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getRxFIFOThreshold(CF_UART_TYPE_PTR uart, uint32_t* RX_FIFO_THRESHOLD_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (RX_FIFO_THRESHOLD_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if RX_FIFO_THRESHOLD_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *RX_FIFO_THRESHOLD_value = uart->RX_FIFO_THRESHOLD;
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_setTxFIFOThreshold(CF_UART_TYPE_PTR uart, uint32_t value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (value > CF_UART_TX_FIFO_THRESHOLD_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if value is out of range
    } else {
        uart->TX_FIFO_THRESHOLD = value;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getTxFIFOThreshold(CF_UART_TYPE_PTR uart, uint32_t* TX_FIFO_THRESHOLD_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (TX_FIFO_THRESHOLD_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if TX_FIFO_THRESHOLD_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *TX_FIFO_THRESHOLD_value = uart->TX_FIFO_THRESHOLD;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getTxCount(CF_UART_TYPE_PTR uart, uint32_t* TX_FIFO_LEVEL_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (TX_FIFO_LEVEL_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if TX_FIFO_LEVEL_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *TX_FIFO_LEVEL_value = uart->TX_FIFO_LEVEL;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getRxCount(CF_UART_TYPE_PTR uart, uint32_t* RX_FIFO_LEVEL_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (RX_FIFO_LEVEL_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if RX_FIFO_LEVEL_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *RX_FIFO_LEVEL_value = uart->RX_FIFO_LEVEL;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_setMatchData(CF_UART_TYPE_PTR uart, uint32_t matchData){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (matchData > CF_UART_MATCH_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if matchData is out of range
    } else {
        uart->MATCH = matchData;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getMatchData(CF_UART_TYPE_PTR uart, uint32_t* MATCH_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (MATCH_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if MATCH_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *MATCH_value = uart->MATCH;
        
    }
    return status;
}

 // Interrupts bits in RIS, MIS, IM, and ICR
 // bit 0: TX FIFO is Empty
 // bit 1: RX FIFO is Full
 // bit 2: TX FIFO level is below the value in the TX FIFO Level Threshold Register
 // bit 3: RX FIFO level is above the value in the RX FIFO Level Threshold Register
 // bit 4: line break
 // bit 5: match
 // bit 6: frame error
 // bit 7: parity error
 // bit 8: overrun 
 // bit 9: timeout 

CF_DRIVER_STATUS CF_UART_getRIS(CF_UART_TYPE_PTR uart, uint32_t* RIS_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (RIS_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if RIS_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *RIS_value = uart->RIS;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getMIS(CF_UART_TYPE_PTR uart, uint32_t* MIS_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (MIS_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if MIS_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *MIS_value = uart->MIS;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_setIM(CF_UART_TYPE_PTR uart, uint32_t mask){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (mask > CF_UART_IM_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if mask is out of range

    } else {
        uart->IM = mask;
        
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_getIM(CF_UART_TYPE_PTR uart, uint32_t* IM_value){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (IM_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if IM_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *IM_value = uart->IM;
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_setICR(CF_UART_TYPE_PTR uart, uint32_t mask){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK; 

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (mask > CF_UART_IC_REG_MAX_VALUE) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if mask is out of range
    } else {
        uart->IC = mask;
        
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_writeChar(CF_UART_TYPE_PTR uart, char data){

    CF_DRIVER_STATUS status = CF_DRIVER_OK;   

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else {

        uint32_t RIS_value;
        do {
            status = CF_UART_getRIS(uart, &RIS_value);
        } while ((status == CF_DRIVER_OK) && (RIS_value & CF_UART_TXB_FLAG) == (uint32_t)0x0); // wait until tx level below flag is 1

        if (status == CF_DRIVER_OK) {
            uart->TXDATA = data;
            status = CF_UART_setICR(uart, CF_UART_TXB_FLAG);
        } else {}
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_writeCharArr(CF_UART_TYPE_PTR uart, const char *char_arr){

    CF_DRIVER_STATUS status = CF_DRIVER_OK;
    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else {
        uint32_t RIS_value;
        char *char_arr_iterator = char_arr;
        while ((status == CF_DRIVER_OK) && (*char_arr_iterator)){
            do {
                status = CF_UART_getRIS(uart, &RIS_value);
            } while ((status == CF_DRIVER_OK) && (RIS_value & CF_UART_TXB_FLAG) == (uint32_t)0x0); // wait until tx level below flag is 1

            if (status == CF_DRIVER_OK) {
                uart->TXDATA = (*(char_arr_iterator));
                char_arr_iterator++;
                status = CF_UART_setICR(uart, CF_UART_TXB_FLAG);
            }else{}
        }
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_readChar(CF_UART_TYPE_PTR uart, char* RXDATA_value){

    CF_DRIVER_STATUS status = CF_DRIVER_OK;

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else {
        uint32_t RIS_value;
        do {
            status = CF_UART_getRIS(uart, &RIS_value);
        } while((status == CF_DRIVER_OK) && (RIS_value & CF_UART_RXA_FLAG) == (uint32_t)0x0); // wait over RX fifo level above flag to be 1

        if (status == CF_DRIVER_OK) {
            *RXDATA_value = uart->RXDATA;
            status = CF_UART_setICR(uart, CF_UART_RXA_FLAG);
        } else {}
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_readCharNonBlocking(CF_UART_TYPE_PTR uart, char* RXDATA_value, bool* data_available){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK;

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else  if (RXDATA_value == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if RXDATA_value is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else if (data_available == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if data_available is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        
        uint32_t RIS_value;
        status = CF_UART_getRIS(uart, &RIS_value);

        // Check if data is available
        if ((status == CF_DRIVER_OK) && (RIS_value & CF_UART_RXA_FLAG) == (uint32_t)0x0) {
            *data_available = false;
        } else {
            *data_available = true;
            *RXDATA_value = uart->RXDATA;
            status = CF_UART_setICR(uart, CF_UART_RXA_FLAG);
        }
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_writeCharNonBlocking(CF_UART_TYPE_PTR uart, char data, bool* data_sent){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK;

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else  if (data_sent == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if data_sent is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        
        uint32_t RIS_value;
        status = CF_UART_getRIS(uart, &RIS_value);

        // Check if data is available
        if ((status == CF_DRIVER_OK) && (RIS_value & CF_UART_TXB_FLAG) == (uint32_t)0x0) {
            *data_sent = false;
        } else {
            *data_sent = true;
            uart->TXDATA = data;
            status = CF_UART_setICR(uart, CF_UART_TXB_FLAG);
        }
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_charsAvailable(CF_UART_TYPE_PTR uart, bool* RXA_flag) {

    CF_DRIVER_STATUS status = CF_DRIVER_OK;
    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (RXA_flag == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if RXA_flag is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        uint32_t RIS_value;
        status = CF_UART_getRIS(uart, &RIS_value);
        if (status == CF_DRIVER_OK) {
            *RXA_flag = (RIS_value & CF_UART_RXA_FLAG) != (uint32_t)0x0;
        }else {}
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_spaceAvailable(CF_UART_TYPE_PTR uart, bool* TXB_flag) {

    CF_DRIVER_STATUS status = CF_DRIVER_OK;
    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                 // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (TXB_flag == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                 // Return CF_DRIVER_ERROR_PARAMETER if TXB_flag is NULL, 
                                                            // i.e. there is no memory location to store the value
    } else {
        uint32_t RIS_value;
        status = CF_UART_getRIS(uart, &RIS_value);
        if (status == CF_DRIVER_OK) {
            *TXB_flag = (RIS_value & CF_UART_TXB_FLAG);     // check if TX FIFO level is below the value in the TX FIFO Level Threshold Register
        }else {}
    }
    return status;
}


CF_DRIVER_STATUS CF_UART_getParityMode(CF_UART_TYPE_PTR uart, uint32_t* parity_mode){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK;
    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (parity_mode == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if parity_mode is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        *parity_mode = (uart->CFG & CF_UART_CFG_REG_PARITY_MASK) >> CF_UART_CFG_REG_PARITY_BIT;
    }
    return status;
}

CF_DRIVER_STATUS CF_UART_busy(CF_UART_TYPE_PTR uart, bool* busy_flag){
    
    CF_DRIVER_STATUS status = CF_DRIVER_OK;
    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (busy_flag == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;                // Return CF_DRIVER_ERROR_PARAMETER if busy_flag is NULL, 
                                                        // i.e. there is no memory location to store the value
    } else {
        uint32_t RIS_value;
        status = CF_UART_getRIS(uart, &RIS_value);
        if (status == CF_DRIVER_OK) {
            *busy_flag = (RIS_value & CF_UART_TXE_FLAG) == (uint32_t)0x0;
        }else {}
    }
    return status;
}


// Function to initialize and configure the UART
CF_DRIVER_STATUS UART_Init(CF_UART_TYPE_PTR uart, uint32_t baud_rate, uint32_t bus_clock, uint32_t data_bits, bool two_stop_bits, enum parity_type parity, uint32_t timeout, uint32_t rx_threshold, uint32_t tx_threshold) {
    CF_DRIVER_STATUS status = CF_DRIVER_OK;

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;    // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    }

    // Calculate and set the prescaler
    uint32_t prescaler = 1;
    if (status == CF_DRIVER_OK) {status = CF_UART_setPrescaler(uart, prescaler);} else {}

    // Configure data bits, stop bits, and parity

    // Set data bits (5-9 bits)
    if (status == CF_DRIVER_OK) {status = CF_UART_setDataSize(uart, data_bits);} else {}

    // Set stop bits (1 or 2)
    if (status == CF_DRIVER_OK) {status = CF_UART_setStopBits(uart, two_stop_bits);} else {}

    // Set parity type
    if (status == CF_DRIVER_OK) {status = CF_UART_setParityType(uart, parity);} else {}

    // Set the receiver timeout value
    if (status == CF_DRIVER_OK) {status = CF_UART_setTimeoutBits(uart, timeout);} else {}

    // Set RX and TX FIFO thresholds
    if (status == CF_DRIVER_OK) {status = CF_UART_setRxFIFOThreshold(uart, rx_threshold);} else {}
    if (status == CF_DRIVER_OK) {status = CF_UART_setTxFIFOThreshold(uart, tx_threshold);} else {}

    // Enable the UART and both RX and TX
    if (status == CF_DRIVER_OK) {status = CF_UART_enable(uart);} else {}
    if (status == CF_DRIVER_OK) {status = CF_UART_setGclkEnable(uart, (uint32_t)1);} else {}
    if (status == CF_DRIVER_OK) {status = CF_UART_enableRx(uart);} else {}
    if (status == CF_DRIVER_OK) {status = CF_UART_enableTx(uart);} else {}

    return status;
}


// Function to receive a string using UART
CF_DRIVER_STATUS CF_UART_readCharArr(CF_UART_TYPE_PTR uart, char *buffer, uint32_t buffer_size) {

    CF_DRIVER_STATUS status = CF_DRIVER_OK;

    if (uart == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;    // Return CF_DRIVER_ERROR_PARAMETER if uart is NULL
    } else if (buffer == NULL) {
        status = CF_DRIVER_ERROR_PARAMETER;    // Return CF_DRIVER_ERROR_PARAMETER if buffer is NULL
    } else if (buffer_size == (uint32_t)0) {
        status = CF_DRIVER_ERROR_PARAMETER;    // Return CF_DRIVER_ERROR_PARAMETER if buffer_size is 0
    }else{
        uint32_t index = 0;
        while (index < (buffer_size - (uint32_t)1)) {
            bool data_available = false;
            status = CF_UART_charsAvailable(uart, &data_available);
            if (status != CF_DRIVER_OK){break;}     // return on error
            if (!data_available) {continue;}        // skip this iteration and wait for data

            char received_char;
            status = CF_UART_readChar(uart, &received_char);
            if (status != CF_DRIVER_OK){break;}     // return on error

            buffer[index] = received_char;
            index++;
            if (received_char == '\n') break;       // Stop reading at newline
        }
        buffer[index] = '\0';                       // Null-terminate the string
    }

    return status;
}



/******************************************************************************
* Static Function Definitions
******************************************************************************/





#endif // CF_UART_C

/******************************************************************************
* End of File
******************************************************************************/