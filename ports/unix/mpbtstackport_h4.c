/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2020 Jim Mussared
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <pthread.h>

#include "py/runtime.h"
#include "py/mperrno.h"
#include "py/mphal.h"

#if MICROPY_PY_BLUETOOTH && MICROPY_BLUETOOTH_BTSTACK && MICROPY_BLUETOOTH_BTSTACK_H4

#include "lib/btstack/chipset/zephyr/btstack_chipset_zephyr.h"

#include "extmod/btstack/btstack_hci_uart.h"
#include "extmod/btstack/modbluetooth_btstack.h"

#define DEBUG_printf(...) // printf(__VA_ARGS__)

STATIC hci_transport_config_uart_t hci_transport_config_uart = {
    HCI_TRANSPORT_CONFIG_UART,
    1000000, // initial baudrate
    0,       // main baudrate
    1,       // flow control
    NULL,    // device name
};

void mp_bluetooth_hci_poll_h4(void) {
    if (mp_bluetooth_btstack_state == MP_BLUETOOTH_BTSTACK_STATE_STARTING || mp_bluetooth_btstack_state == MP_BLUETOOTH_BTSTACK_STATE_ACTIVE) {
        mp_bluetooth_btstack_hci_uart_process();
    }
}

void mp_bluetooth_btstack_port_init_h4(void) {
    DEBUG_printf("mp_bluetooth_btstack_port_init_h4\n");

    const hci_transport_t *transport = hci_transport_h4_instance(&mp_bluetooth_btstack_hci_uart_block);
    hci_init(transport, &hci_transport_config_uart);

    hci_set_chipset(btstack_chipset_zephyr_instance());
}

void mp_bluetooth_btstack_port_deinit(void) {
    DEBUG_printf("mp_bluetooth_btstack_port_deinit\n");

    hci_power_control(HCI_POWER_OFF);
    hci_close();
}

void mp_bluetooth_btstack_port_start(void) {
    DEBUG_printf("mp_bluetooth_btstack_port_start\n");

    hci_power_control(HCI_POWER_ON);
}

#endif // MICROPY_PY_BLUETOOTH && MICROPY_BLUETOOTH_BTSTACK && MICROPY_BLUETOOTH_BTSTACK_H4
