#include "global.h"

void sub_08006BE4(u16);
void sub_08036934(const void *, void *);
void sub_080351EC(void *, void *, u32);

extern u32 gUnk_08D536F0[];
extern u32 gUnk_08D536C8[];
extern u8  gUnk_02018800[];
extern u8  gUnk_02020B00[];

void sub_080351A4(void *a, u16 b)
{
    sub_08006BE4(b);
    sub_08036934((const void *)gUnk_08D536F0[b], gUnk_02018800);
    sub_080351EC(a, gUnk_02018800, gUnk_08D536C8[gUnk_02020B00[0x19]]);
}
