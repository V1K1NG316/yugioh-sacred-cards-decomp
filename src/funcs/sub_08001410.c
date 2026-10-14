#include "global.h"

void sub_080284A0(void);
void sub_08003BC4(void);

extern u16 gUnk_0202345C;
extern u16 gUnk_02023464;
extern volatile u16 gUnk_0201FCAC;

void sub_08001410(void)
{
    gUnk_0202345C = 0xFC;
    gUnk_02023464 = 8;
    sub_080284A0();
    sub_08003BC4();
    while ((gUnk_0201FCAC & 0x3FF) == 0)
        sub_08003BC4();
    sub_08003BC4();
}
