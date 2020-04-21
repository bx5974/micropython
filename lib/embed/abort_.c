#include <py/runtime.h>

#include "py/misc.h"
#include "py/mpconfig.h"
#include "py/obj.h"

NORETURN void abort_(void);

NORETURN void abort_(void) {
    mp_raise_msg(&mp_type_RuntimeError, MP_ERROR_TEXT("abort() called"));
}
