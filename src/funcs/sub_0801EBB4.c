#include "global.h"

void sub_08028438(void);
void sub_0803692C(u32, u32, u32);

extern u8 gUnk_02007440[];

void sub_0801EBB4(void)
{
    u8 *base;

    sub_08028438();
    base = gUnk_02007440;
    sub_0803692C((u32)base, 0x06007040, 0xE00);
    sub_0803692C((u32)(base - 0x7000), 0x06000040, 0xE00);
    sub_0803692C((u32)(base - 0x5400), 0x06001C40, 0xE00);
    sub_0803692C((u32)(base - 0x3800), 0x06003840, 0xE00);
    sub_0803692C((u32)(base - 0x1C00), 0x06005440, 0xE00);
    sub_0803692C(0x02000160, 0x05000160, 0x20);
    sub_0803692C((u32)(base + 0x84E0), 0x0600F520, 0xE00);
}
