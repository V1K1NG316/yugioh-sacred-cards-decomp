#include "global.h"

void sub_0802832C(u16 *, u16);
void sub_08023FD4(u16 *);

extern u32 gUnk_02023260[];

void sub_08028308(u16 *p, u8 a)
{
    sub_0802832C((u16 *)gUnk_02023260[a], *p);
    sub_08023FD4(p);
}
