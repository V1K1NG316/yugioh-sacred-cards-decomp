#include "global.h"

extern u8 *gUnk_08D36418;

void sub_08018618(void)
{
    if (gUnk_08D36418[5] != 0)
        gUnk_08D36418[5]--;
}
