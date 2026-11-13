#ifdef KERNEL_STATIC
#include M2S(INCLUDE_PATH/inc_a.h)
#else
#include "inc_b.h"
#endif
constant char c = '\
n';
#error probe_line_8
