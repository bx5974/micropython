#ifndef MICROPY_INCLUDED_EXTMOD_NIMBLE_SYSCFG_H
#define MICROPY_INCLUDED_EXTMOD_NIMBLE_SYSCFG_H

#include "py/mphal.h"

#include "mpnimbleport.h"

void *nimble_malloc(size_t size);
void nimble_free(void *ptr);
void *nimble_realloc(void *ptr, size_t size);

// Redirect NimBLE malloc to the GC heap.
#define malloc(size) nimble_malloc(size)
#define free(ptr) nimble_free(ptr)
#define realloc(ptr, size) nimble_realloc(ptr, size)

int nimble_sprintf(char *str, const char *fmt, ...);
#define sprintf(str, fmt, ...) nimble_sprintf(str, fmt, __VA_ARGS__)

#define MYNEWT_VAL(x) MYNEWT_VAL_ ## x

#define MYNEWT_VAL_LOG_LEVEL (255)

/*** compiler/arm-none-eabi-m4 */
#define MYNEWT_VAL_HARDFLOAT (1)

/*** kernel/os */
#define MYNEWT_VAL_FLOAT_USER (0)
#define MYNEWT_VAL_MSYS_1_BLOCK_COUNT (12)
#define MYNEWT_VAL_MSYS_1_BLOCK_SIZE (292)
#define MYNEWT_VAL_MSYS_2_BLOCK_COUNT (0)
#define MYNEWT_VAL_MSYS_2_BLOCK_SIZE (0)
#define MYNEWT_VAL_OS_CPUTIME_FREQ (1000000)
#define MYNEWT_VAL_OS_CPUTIME_TIMER_NUM (0)
#define MYNEWT_VAL_OS_CTX_SW_STACK_CHECK (0)
#define MYNEWT_VAL_OS_CTX_SW_STACK_GUARD (4)
#define MYNEWT_VAL_OS_MAIN_STACK_SIZE (1024)
#define MYNEWT_VAL_OS_MAIN_TASK_PRIO (127)
#define MYNEWT_VAL_OS_MEMPOOL_CHECK (0)
#define MYNEWT_VAL_OS_MEMPOOL_POISON (0)

/*** nimble */
#define MYNEWT_VAL_BLE_EXT_ADV (0)
#define MYNEWT_VAL_BLE_EXT_ADV_MAX_SIZE (31)
#define MYNEWT_VAL_BLE_MAX_CONNECTIONS (4)
#define MYNEWT_VAL_BLE_MULTI_ADV_INSTANCES (0)
#define MYNEWT_VAL_BLE_ROLE_BROADCASTER (1)
#define MYNEWT_VAL_BLE_ROLE_CENTRAL (1)
#define MYNEWT_VAL_BLE_ROLE_OBSERVER (1)
#define MYNEWT_VAL_BLE_ROLE_PERIPHERAL (1)
#define MYNEWT_VAL_BLE_WHITELIST (1)

/*** nimble/host */
#define MYNEWT_VAL_BLE_ATT_PREFERRED_MTU (256)
#define MYNEWT_VAL_BLE_ATT_SVR_FIND_INFO (1)
#define MYNEWT_VAL_BLE_ATT_SVR_FIND_TYPE (1)
#define MYNEWT_VAL_BLE_ATT_SVR_INDICATE (1)
#define MYNEWT_VAL_BLE_ATT_SVR_MAX_PREP_ENTRIES (64)
#define MYNEWT_VAL_BLE_ATT_SVR_NOTIFY (1)
#define MYNEWT_VAL_BLE_ATT_SVR_QUEUED_WRITE (1)
#define MYNEWT_VAL_BLE_ATT_SVR_QUEUED_WRITE_TMO (30000)
#define MYNEWT_VAL_BLE_ATT_SVR_READ (1)
#define MYNEWT_VAL_BLE_ATT_SVR_READ_BLOB (1)
#define MYNEWT_VAL_BLE_ATT_SVR_READ_GROUP_TYPE (1)
#define MYNEWT_VAL_BLE_ATT_SVR_READ_MULT (1)
#define MYNEWT_VAL_BLE_ATT_SVR_READ_TYPE (1)
#define MYNEWT_VAL_BLE_ATT_SVR_SIGNED_WRITE (1)
#define MYNEWT_VAL_BLE_ATT_SVR_WRITE (1)
#define MYNEWT_VAL_BLE_ATT_SVR_WRITE_NO_RSP (1)
#define MYNEWT_VAL_BLE_GAP_MAX_PENDING_CONN_PARAM_UPDATE (1)
#define MYNEWT_VAL_BLE_GATT_DISC_ALL_CHRS (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_DISC_ALL_DSCS (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_DISC_ALL_SVCS (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_DISC_CHR_UUID (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_DISC_SVC_UUID (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_FIND_INC_SVCS (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_INDICATE (1)
#define MYNEWT_VAL_BLE_GATT_MAX_PROCS (4)
#define MYNEWT_VAL_BLE_GATT_NOTIFY (1)
#define MYNEWT_VAL_BLE_GATT_READ (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_READ_LONG (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_READ_MAX_ATTRS (8)
#define MYNEWT_VAL_BLE_GATT_READ_MULT (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_READ_UUID (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_RESUME_RATE (1000)
#define MYNEWT_VAL_BLE_GATT_SIGNED_WRITE (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_WRITE (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_WRITE_LONG (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_WRITE_MAX_ATTRS (4)
#define MYNEWT_VAL_BLE_GATT_WRITE_NO_RSP (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_GATT_WRITE_RELIABLE (MYNEWT_VAL_BLE_ROLE_CENTRAL)
#define MYNEWT_VAL_BLE_HOST (1)
#define MYNEWT_VAL_BLE_HS_AUTO_START (1)
#define MYNEWT_VAL_BLE_HS_DEBUG (0)
#define MYNEWT_VAL_BLE_HS_FLOW_CTRL (0)
#define MYNEWT_VAL_BLE_HS_FLOW_CTRL_ITVL (1000)
#define MYNEWT_VAL_BLE_HS_FLOW_CTRL_THRESH (2)
#define MYNEWT_VAL_BLE_HS_FLOW_CTRL_TX_ON_DISCONNECT (0)
#define MYNEWT_VAL_BLE_HS_PHONY_HCI_ACKS (0)
#define MYNEWT_VAL_BLE_HS_REQUIRE_OS (1)
#define MYNEWT_VAL_BLE_HS_STOP_ON_SHUTDOWN_TIMEOUT (2000)
#define MYNEWT_VAL_BLE_L2CAP_COC_MAX_NUM (1)
#define MYNEWT_VAL_BLE_L2CAP_COC_MPS (MYNEWT_VAL_MSYS_1_BLOCK_SIZE-8)
#define MYNEWT_VAL_BLE_L2CAP_ENHANCED_COC (0)
#define MYNEWT_VAL_BLE_L2CAP_JOIN_RX_FRAGS (1)
#define MYNEWT_VAL_BLE_L2CAP_MAX_CHANS (3*MYNEWT_VAL_BLE_MAX_CONNECTIONS)
#define MYNEWT_VAL_BLE_L2CAP_RX_FRAG_TIMEOUT (30000)
#define MYNEWT_VAL_BLE_L2CAP_SIG_MAX_PROCS (1)
#define MYNEWT_VAL_BLE_MONITOR_CONSOLE_BUFFER_SIZE (128)
#define MYNEWT_VAL_BLE_MONITOR_RTT (0)
#define MYNEWT_VAL_BLE_MONITOR_RTT_BUFFERED (1)
#define MYNEWT_VAL_BLE_MONITOR_RTT_BUFFER_NAME ("monitor")
#define MYNEWT_VAL_BLE_MONITOR_RTT_BUFFER_SIZE (256)
#define MYNEWT_VAL_BLE_MONITOR_UART (0)
#define MYNEWT_VAL_BLE_MONITOR_UART_BAUDRATE (1000000)
#define MYNEWT_VAL_BLE_MONITOR_UART_BUFFER_SIZE (64)
#define MYNEWT_VAL_BLE_MONITOR_UART_DEV ("uart0")
#define MYNEWT_VAL_BLE_RPA_TIMEOUT (300)
#define MYNEWT_VAL_BLE_SM_BONDING (0)
#define MYNEWT_VAL_BLE_SM_IO_CAP (BLE_HS_IO_NO_INPUT_OUTPUT)
#define MYNEWT_VAL_BLE_SM_KEYPRESS (0)
#define MYNEWT_VAL_BLE_SM_LEGACY (1)
#define MYNEWT_VAL_BLE_SM_MAX_PROCS (1)
#define MYNEWT_VAL_BLE_SM_MITM (0)
#define MYNEWT_VAL_BLE_SM_OOB_DATA_FLAG (0)
#define MYNEWT_VAL_BLE_SM_OUR_KEY_DIST (0)
#define MYNEWT_VAL_BLE_SM_SC (1)
#define MYNEWT_VAL_BLE_SM_THEIR_KEY_DIST (0)
#define MYNEWT_VAL_BLE_STORE_MAX_BONDS (3)
#define MYNEWT_VAL_BLE_STORE_MAX_CCCDS (8)

/*** nimble/host/services/gap */
#define MYNEWT_VAL_BLE_SVC_GAP_APPEARANCE (0)
#define MYNEWT_VAL_BLE_SVC_GAP_APPEARANCE_WRITE_PERM (-1)
#define MYNEWT_VAL_BLE_SVC_GAP_CENTRAL_ADDRESS_RESOLUTION (-1)
#define MYNEWT_VAL_BLE_SVC_GAP_DEVICE_NAME ("pybd")
#define MYNEWT_VAL_BLE_SVC_GAP_DEVICE_NAME_MAX_LENGTH (31)
#define MYNEWT_VAL_BLE_SVC_GAP_DEVICE_NAME_WRITE_PERM (-1)
#define MYNEWT_VAL_BLE_SVC_GAP_PPCP_MAX_CONN_INTERVAL (0)
#define MYNEWT_VAL_BLE_SVC_GAP_PPCP_MIN_CONN_INTERVAL (0)
#define MYNEWT_VAL_BLE_SVC_GAP_PPCP_SLAVE_LATENCY (0)
#define MYNEWT_VAL_BLE_SVC_GAP_PPCP_SUPERVISION_TMO (0)

/* Overridden by targets/porting-nimble (defined by nimble/transport) */
#define MYNEWT_VAL_BLE_HCI_TRANSPORT_NIMBLE_BUILTIN (0)
#define MYNEWT_VAL_BLE_HCI_TRANSPORT_RAM (0)
#define MYNEWT_VAL_BLE_HCI_TRANSPORT_SOCKET (0)
#define MYNEWT_VAL_BLE_HCI_TRANSPORT_UART (1)

/*** nimble/transport/uart */
#define MYNEWT_VAL_BLE_ACL_BUF_COUNT (12)
#define MYNEWT_VAL_BLE_ACL_BUF_SIZE (255)
#define MYNEWT_VAL_BLE_HCI_ACL_OUT_COUNT (12)
#define MYNEWT_VAL_BLE_HCI_EVT_BUF_SIZE (70)
#define MYNEWT_VAL_BLE_HCI_EVT_HI_BUF_COUNT (8)
#define MYNEWT_VAL_BLE_HCI_EVT_LO_BUF_COUNT (8)

/* Overridden by targets/porting-nimble (defined by nimble/transport/uart) */
#define MYNEWT_VAL_BLE_HCI_UART_BAUD (MICROPY_HW_BLE_UART_BAUDRATE)
#define MYNEWT_VAL_BLE_HCI_UART_DATA_BITS (8)
#define MYNEWT_VAL_BLE_HCI_UART_FLOW_CTRL (1)
#define MYNEWT_VAL_BLE_HCI_UART_PARITY (HAL_UART_PARITY_NONE)
#define MYNEWT_VAL_BLE_HCI_UART_PORT (MICROPY_HW_BLE_UART_ID)
#define MYNEWT_VAL_BLE_HCI_UART_STOP_BITS (1)

/* Required for code that uses BLE_HS_LOG */
#define MYNEWT_VAL_NEWT_FEATURE_LOGCFG (1)

#endif // MICROPY_INCLUDED_EXTMOD_NIMBLE_SYSCFG_H
