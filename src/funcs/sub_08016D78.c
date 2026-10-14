#include "global.h"

u32 sub_0803691C(void);
void sub_080181F4(u32);
void sub_08021F10(u32);
void sub_08017F44(void *);
void sub_08021E50(u32);
void sub_08017E74(void *);

void sub_08016D78(void)
{
    u8 buf[0xC];

    sub_080181F4(sub_0803691C() == 0);
    sub_08021F10(4);
    sub_08017F44(buf);
    buf[8] = 0x11;
    sub_08021E50(0x52);
    sub_08017E74(buf);
}
