#include "global.h"

extern u8 gUnk_02020D88[];
extern u8 gUnk_02020D30[];

void sub_08016234(void);
void sub_08021F10(u32);
void sub_08017DA8(void);

void sub_08017D6C(void)
{
    if (gUnk_02020D88[1] == 2)
        gUnk_02020D30[0x29] = 1;
    else
        gUnk_02020D30[0x29] = 2;
    sub_08016234();
    sub_08021F10(2);
    sub_08017DA8();
}
