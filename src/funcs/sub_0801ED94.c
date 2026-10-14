#include "global.h"

void sub_080285C8(void);
void sub_080284E4(void);
void sub_080284A0(void);
void sub_08028438(void);

void sub_0801ED94(void)
{
    sub_080285C8();
    sub_080284E4();
    sub_080284A0();
    sub_08028438();
    *(u16 *)0x04000000 = 0x9E00;
}
