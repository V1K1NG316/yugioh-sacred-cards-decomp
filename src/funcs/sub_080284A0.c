#include "global.h"

extern u16 gUnk_0202345C[];
extern u16 gUnk_02023468[];
extern u16 gUnk_02023464[];

void sub_080284A0(void)
{
    *(u16 *)0x04000050 = gUnk_0202345C[0];
    *(u16 *)0x04000052 = gUnk_02023468[0];
    *(u16 *)0x04000054 = gUnk_02023464[0];
}
