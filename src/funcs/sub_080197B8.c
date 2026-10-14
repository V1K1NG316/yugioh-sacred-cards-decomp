#include "global.h"

void sub_0803692C(const void *, void *, u32);

extern u8 gUnk_08D3816C[];
extern u8 gUnk_02004400[];
extern u8 gUnk_08D3912C[];

void sub_080197B8(void)
{
    u8 *dst;
    u8 *src;
    u32 i;

    sub_0803692C(gUnk_08D3816C, dst = gUnk_02004400, 0x7E0);
    i = 0;
    src = gUnk_08D3912C;
    dst += 0xB000;
    do {
        sub_0803692C(src, dst, 0x20);
        src += 0x40;
        dst += 0x40;
        i++;
    } while (i <= 0x13);
}
