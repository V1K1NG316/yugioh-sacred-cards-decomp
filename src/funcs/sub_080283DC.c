#include "global.h"

u32 sub_08023C34(u16);
u32 sub_08018150(u16);

extern u8 gUnk_02023448[];

u32 sub_080283DC(u16 a)
{
    u32 v;

    if (sub_08023C34(a) == 4) {
        v = (u8)sub_08018150(a) - gUnk_02023448[0];
        if ((s32)v < 0)
            v = 0;
        v = (u8)v;
    } else {
        v = 0;
    }
    return v;
}
