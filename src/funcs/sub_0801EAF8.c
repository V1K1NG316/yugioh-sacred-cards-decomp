#include "global.h"

void sub_0803692C(u32, u32, u32);

void sub_0801EAF8(u8 page)
{
    u32 off = page * 0x1C00;
    u8 *p = (u8 *)0x02000440;

    sub_0803692C((u32)(p + off), 0x06000040 + off, 0xE00);
    sub_0803692C(0x02000160, 0x05000160, 0x20);
    sub_0803692C((u32)(p + 0xF4E0), 0x0600F520, 0xE00);
    sub_0803692C((u32)(p + 0x9FC0), 0x0600A000, 0x400);
}
