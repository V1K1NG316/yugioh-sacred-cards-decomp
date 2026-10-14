#include "global.h"

void sub_08024DB8(u8 *);

extern u8 gUnk_02018400[];

void sub_080306FC(void)
{
    u8 i = 0;

    do {
        sub_08024DB8(gUnk_02018400 + i * 8);
        i++;
    } while (i < 0x80);
}
