#include "global.h"

void sub_08036934(const void *, void *);
void sub_0803692C(const void *, void *, u32);

extern u8 gUnk_02000000[];

void sub_08004878(void)
{
    u8 i;

    sub_08036934((const void *)0x0807F458, (void *)0x02000400);
    for (i = 0; i <= 0x13; i++)
        sub_0803692C((const void *)(0x08081B2C + i * 60), (void *)(0x02003C00 + i * 64),
                     0x0400000F);
    sub_0803692C((const void *)0x0808248C, (void *)gUnk_02000000, 0x04000020);
}
