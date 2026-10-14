#include "global.h"

void sub_08036934(const void *, void *);
void sub_0803692C(const void *, void *, u32);
void sub_08003BC4(void);
void sub_08030DD8(void);

void sub_08031B0C(void)
{
    u8 *p;

    sub_08036934((void *)0x082B26AC, p = (u8 *)0x0200DC00);
    sub_0803692C((void *)0x082B2868, p += 0x1000, 0x280);
    sub_08003BC4();
    sub_08030DD8();
}
