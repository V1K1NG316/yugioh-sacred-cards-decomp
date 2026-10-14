#include "global.h"

extern u8 gUnk_02023284[];
extern u8 *gUnk_08D34AB4;

u32 sub_080268FC(u8 *);
u32 sub_0802712C(u32);

void sub_0800FFF0(void)
{
    if (sub_080268FC(gUnk_02023284) == 5) {
        *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
    } else {
        if ((u8)sub_0802712C(2) != 1) {
            *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EE0ACE9;
        } else {
            *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7EED7E3C;
        }
    }
}
