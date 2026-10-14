#include "global.h"

extern u8 gUnk_02023120[];
extern u8 gUnk_02023140[];

void sub_08023200(u8);
void sub_08023CB4(void);

void sub_0802341C(void)
{
    u16 *p;

    sub_08023CB4();
    p = (u16 *)gUnk_02023120;
    if (p[9] <= p[1]) {
        p[9] = 0;
        sub_08023200(gUnk_02023120[0x1B]);
    } else {
        p[9] -= p[1];
    }
    gUnk_02023140[0x18] = 0xA;
}
