#include "global.h"

extern u8 *gUnk_08D36418;

void sub_0801892C(void)
{
    u8 *s = gUnk_08D36418;
    register u32 v asm("r0"); /* FAKEMATCH: the ROM keeps the counter in r0 and the pointer in r1 */

    v = s[0];
    if (v > 6)
        v = 0;
    else
        v++;
    s[0] = v;
}
