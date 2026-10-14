#include "global.h"

extern u32 gUnk_08D4BBF4[];
extern u32 gUnk_08D4BBF8[];

void sub_08023064(u8, u32, u16);
void sub_0803692C(u32, u32, u32);

void sub_08022744(void)
{
    sub_08023064(0, gUnk_08D4BBF4[0], 0x100);
    sub_0803692C(gUnk_08D4BBF8[0], 0x02000200, 0x04000018);
}
