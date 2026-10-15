#include "global.h"

void sub_0803692C(u32, u32, u32);
void sub_08008E78(void);

extern u16 *gUnk_08D36680[];
extern u8 gUnk_02020B00[];

void sub_0801916C(void)
{
    u8 n = gUnk_02020B00[0x18];
    u32 off;

    if (n == 0)
        return;

    if (n > 0x0C)
        n = 0x0C;

    sub_0803692C(0x08948BBC, 0x02020B80, 0x04000010);

    while (n != 0) {
        off = (0x72 - n) * 0x40;
        sub_0803692C((u32)gUnk_08D36680[0] + off, 0x02020B40, 0x04000010);
        sub_08008E78();
        sub_0803692C(0x02020BC0, (u32)gUnk_08D36680[0] + off, 0x04000010);
        n--;
    }
}
