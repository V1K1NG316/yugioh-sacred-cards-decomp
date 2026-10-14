#include "global.h"

void sub_0802832C(u16 *, u16);
void sub_08023FD4(u16 *);

extern u16 gUnk_02023254[];

void sub_080282E4(u16 *p, u8 a)
{
    sub_0802832C(gUnk_02023254 + a * 2, *p);
    sub_08023FD4(p);
}
