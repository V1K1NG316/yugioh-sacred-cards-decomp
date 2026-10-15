#include "global.h"

void sub_0801C114(s16);
void sub_0801C26C(void);
void sub_0801C184(void);
void sub_0801C1F0(u8);
void sub_0801DF54(u8);
void sub_0801E138(void);

extern u8 gUnk_020214D0[];

void sub_0801BFE4(void)
{
    u8 *p = gUnk_020214D0;

    if ((s8)p[0x7E7] > 1) {
        p[0x7E7]--;
    } else {
        sub_0801C114(-1);
        sub_0801C26C();
        sub_0801C184();
        sub_0801C1F0(0);
        sub_0801DF54(0);
        sub_0801E138();
    }
}
