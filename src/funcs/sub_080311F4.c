#include "global.h"

void sub_08031438(u8, u8);
void sub_080318FC(void);

extern u8 gUnk_02023490[];

void sub_080311F4(u8 n)
{
    u8 *base;

    sub_08031438(0, n);
    sub_080318FC();
    base = gUnk_02023490;
    if (*(u8 *)(base + 0x264) != 2) {
        sub_08031438(0, n);
        sub_080318FC();
    }
    if (*(u8 *)(base + 0x20) == 1)
        *(u8 *)(base + 0x20) = 2;
}
