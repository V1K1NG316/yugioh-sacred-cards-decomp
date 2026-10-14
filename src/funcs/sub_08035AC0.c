#include "global.h"

extern u16 gUnk_04000204;

void sub_08003958(void);
void sub_080039A4(void);
void sub_08003B18(void);

void sub_08035AC0(void)
{
    gUnk_04000204 = 0x4014;
    sub_08003958();
    sub_080039A4();
    sub_08003B18();
}
