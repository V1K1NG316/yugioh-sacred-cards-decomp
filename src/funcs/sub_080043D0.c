#include "global.h"

extern u8 gUnk_02020770[];
extern u8 gUnk_0808673C[];

void sub_080043D0(void)
{
    u32 i;

    for (i = 0; i <= 900; i++)
        gUnk_02020770[i] = gUnk_0808673C[i];
}
