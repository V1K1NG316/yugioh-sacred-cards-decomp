#include "global.h"

void sub_0803692C(const void *, void *, u32);
void sub_080284CC(void);

void sub_08030DD8(void)
{
    u8 *p = (u8 *)0x0200DC00;

    sub_0803692C(p, (void *)0x0600D800, 0x04000388);
    p += 0x1000;
    sub_0803692C(p, (void *)0x0600E800, 0x04000040);
    sub_080284CC();
}
