#include "global.h"

extern u32 gUnk_08D3618C[];
extern u16 gUnk_02020D30[];

void sub_08017ED4(void);
void sub_08024F2C(u32, u32, u32, u32, u32);

void sub_08017EA4(void)
{
    sub_08017ED4();
    sub_08024F2C(gUnk_08D3618C[gUnk_02020D30[8]], 0, 0, 0, 0);
}
