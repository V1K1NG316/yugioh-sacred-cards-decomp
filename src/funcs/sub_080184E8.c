#include "global.h"

extern u16 gUnk_0202345C;
extern u16 gUnk_02023464;

void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_080284A0(void);

void sub_080184E8(void)
{
    u16 i;

    gUnk_0202345C = 0xFF;
    for (i = 0; i <= 0xF; i++) {
        gUnk_02023464 = i & 0x1F;
        sub_08003B58((void *)sub_080284A0);
        sub_08003BC4();
    }
}
