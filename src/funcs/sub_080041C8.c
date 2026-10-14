#include "global.h"

void sub_0803692C(const void *, void *, u32);

extern u32 gUnk_08D30DFC[];
extern u8 *gUnk_0201CB28;

void sub_080041C8(u8 a, u8 *b)
{
    if ((u8)(a + 0xEB) <= 2) {
        sub_0803692C((const void *)gUnk_08D30DFC[a], b, 0x20);
        sub_0803692C((const void *)(gUnk_08D30DFC[a] + 0x80), b + 0x40, 0x20);
        sub_0803692C((const void *)(gUnk_08D30DFC[a] + 0x40), gUnk_0201CB28, 0x20);
        sub_0803692C((const void *)(gUnk_08D30DFC[a] + 0xC0), gUnk_0201CB28 + 0x40, 0x20);
    } else {
        sub_0803692C((const void *)gUnk_08D30DFC[a], b, 0x40);
    }
}
