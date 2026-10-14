#include "global.h"

extern u8 gUnk_02000000[];

void sub_0803692C(const void *, void *, u32);
void sub_08001550(void);
void sub_08003B58(void *);
void sub_08028580(void);
void sub_0802854C(void);
void sub_080284E4(void);
void sub_08003BC4(void);

void sub_080014F8(void)
{
    sub_0803692C((const void *)0x0806F480, gUnk_02000000, 0x10);
    sub_0803692C((const void *)0x0806F4A0, gUnk_02000000 + 0x200, 0x10);
    sub_08001550();
    sub_08003B58((void *)0x080016CD);
    sub_08028580();
    sub_0802854C();
    sub_080284E4();
    sub_08003B58((void *)0x080016B1);
    sub_08003BC4();
}
