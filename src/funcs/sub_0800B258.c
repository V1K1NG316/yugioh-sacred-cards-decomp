#include "global.h"

extern volatile u16 gUnk_0202347C[];
extern u8 gUnk_080AAED0[];
extern u8 *gUnk_08D34AB4;

u32 sub_0803691C(void);

void sub_0800B258(void)
{
    if (gUnk_0202347C[gUnk_080AAED0[sub_0803691C()]] <= 1000) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FFFFFFF;
    } else {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FF99749;
    }
}
