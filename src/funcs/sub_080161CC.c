#include "global.h"

void sub_080285D8(void);
void sub_080284A0(void);
void sub_08028438(void);

void sub_080161CC(void)
{
    sub_080285D8();
    ((u16 *)0x0400000A)[0] = 0x1D81;
    ((u16 *)0x0400000A)[1] = 0x1E06;
    ((u16 *)0x0400000A)[2] = 0x1F0B;
    sub_080284A0();
    sub_08028438();
}
