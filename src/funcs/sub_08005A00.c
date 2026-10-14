#include "global.h"

void sub_0803692C(const void *, void *, u32);

void sub_08005A00(void)
{
    u8 *p;
    u8 *q;
    const u8 *s;

    sub_0803692C((const void *)0x08087EFC, p = (u8 *)0x02000362, 0x10);
    sub_0803692C((const void *)0x08086EFC, q = (u8 *)0x02014800, 0x04000400);
    sub_0803692C((const void *)0x08087FBC, p + 0x1E, 0x10);
    s = (const u8 *)0x08087F3C;
    sub_0803692C(s, q - 0x2000, 0x20);
    s += 0x40;
    sub_0803692C(s, q - 0x1C00, 0x20);
}
