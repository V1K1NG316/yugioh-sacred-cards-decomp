#include "global.h"

void sub_0801715C(u32, u32, u32);
u32 sub_0802761C(u8, u8);

extern u8 gUnk_02023438[];
extern u8 gUnk_02008A00[];

void sub_08025BE0(void)
{
    if (sub_0802761C(gUnk_02023438[1], gUnk_02023438[0]) == 0)
        sub_0801715C((u32)gUnk_02008A00, 0x08D4C2E7, 0x801);
    else
        sub_0801715C((u32)gUnk_02008A00, 0x08D4C337, 0x801);
}
