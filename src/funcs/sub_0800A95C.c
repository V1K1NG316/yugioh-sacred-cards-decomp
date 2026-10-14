#include "global.h"

extern u8 *gUnk_08D34AB4;

u32 sub_08018208(u32);
u32 sub_08018218(void);
u32 sub_0803691C(void);

void sub_0800A95C(void)
{
    if (*(u32 *)(gUnk_08D34AB4 + 0x14F0) != 0x7EE0ACE9) {
        if ((u8)sub_08018218() == 1) {
            if ((u8)sub_08018208((u8)sub_0803691C()) == 2)
                *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0;
            else
                *(u32 *)(gUnk_08D34AB4 + 0x14F0) = 0x7FFFFFFF;
        }
    }
}
