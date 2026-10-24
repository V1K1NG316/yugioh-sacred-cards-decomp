#include "global.h"

extern u8 *gUnk_08D36418;

void sub_08018670(void)
{
    u8 *p = gUnk_08D36418;
    register u32 v asm("r0"); /* FAKEMATCH: the ROM keeps the counter in r0 and the pointer in r1 */

    v = p[4];
    if (v > 0x1D)
        v = 0;
    else
        v++;
    p[4] = v;
}
