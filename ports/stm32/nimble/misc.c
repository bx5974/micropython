/*
 * This file is part of the MicroPython project, http://micropython.org/
 *
 * The MIT License (MIT)
 *
 * Copyright (c) 2018-2019 Damien P. George
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

#include "py/runtime.h"

#if MICROPY_BLUETOOTH_NIMBLE

/******************************************************************************/
// Misc functions needed by Nimble

#include <stdarg.h>

int sprintf(char *str, const char *fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    int ret = vsnprintf(str, 65535, fmt, ap);
    va_end(ap);
    return ret;
}

// TODO: deal with root pointers
// TODO: deal with soft reset

void *malloc(size_t size) {
    printf("NIMBLE malloc(%u)\n", (uint)size);
    void *ptr = m_malloc(size);
    printf(" --> 0x%p\n", ptr);
    return ptr;
}

void free(void *ptr) {
    printf("NIMBLE free(0x%p)\n", ptr);
    return m_free(ptr);
}

void *realloc(void *ptr, size_t size) {
    printf("NIMBLE realloc(%p, %u)\n", ptr, (uint)size);
    ptr = m_realloc(ptr, size);
    printf(" --> 0x%p\n", ptr);
    return ptr;
}

#endif
