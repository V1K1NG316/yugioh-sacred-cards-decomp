#include "global.h"

extern u16 gUnk_08D4BE50[];
extern u8 gUnk_02010400[];
extern u8 gUnk_080D4694[];
extern u8 gUnk_080D4894[];
extern u8 gUnk_02000340[];

void sub_080245D0(u8 *, u8 *);
void sub_0802460C(void);
void sub_0803692C(u32, u32, u32);

void sub_08024598(void)
{
    sub_080245D0(gUnk_02010400 + gUnk_08D4BE50[3] * 32, gUnk_080D4694);
    sub_0803692C((u32)gUnk_080D4894, (u32)gUnk_02000340, 0x10);
    sub_0802460C();
}
