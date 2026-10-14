#include "global.h"

void sub_08037588(u8 *, u8 *);

void sub_080381CC(u8 *p)
{
    u32 ident = *(u32 *)(p + 0x34);

    if (ident == 0x68736D53) {
        s32 n;
        u8 *q;

        *(u32 *)(p + 0x34) = ident + 1;
        *(u32 *)(p + 4) |= 0x80000000;
        n = *(u8 *)(p + 8);
        q = *(u8 **)(p + 0x2c);
        while (n > 0) {
            sub_08037588(p, q);
            n--;
            q += 0x50;
        }
        *(u32 *)(p + 0x34) = 0x68736D53;
    }
}
