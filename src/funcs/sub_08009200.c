#include "global.h"

extern u16 gUnk_02020C30[];
extern u32 gUnk_08D349EC[];

void sub_08023C8C(void);
void sub_08038E24(u32);

void sub_08009200(void)
{
    sub_08023C8C();
    sub_08038E24(gUnk_08D349EC[gUnk_02020C30[0]]);
}
