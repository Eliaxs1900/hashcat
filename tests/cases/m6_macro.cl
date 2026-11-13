#ifdef USE_BS
#define COMPARE_M M2S(INCLUDE_PATH/inc_multi_bs.cl)
#else
#define COMPARE_M M2S(INCLUDE_PATH/inc_multi.cl)
#endif
#include COMPARE_M
