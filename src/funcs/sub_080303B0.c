#include "global.h"

void sub_0803692C(const void *, void *, u32);

extern u8 gUnk_02023490[];
extern u8 *gUnk_08D516A0[];
extern u16 gUnk_02023474[];
extern u16 gUnk_02023450[];

void sub_080303B0(void)
{
    *(u16 *)0x0400000C = 0x1E82;
    *gUnk_02023474 = 8;
    *gUnk_02023450 = 0;
    sub_0803692C(gUnk_08D516A0[*(u16 *)gUnk_02023490], (void *)0x0200F400, 0x400);
}
