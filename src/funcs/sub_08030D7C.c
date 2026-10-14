#include "global.h"

void sub_08003BC4(void);
void sub_08036928(const void *, void *, u32);
void sub_080284E4(void);

void sub_08030D7C(void)
{
    sub_08003BC4();
    sub_08036928((void *)0x02010400, (void *)0x06010000, 0x800);
    sub_080284E4();
}
