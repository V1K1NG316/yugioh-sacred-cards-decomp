#include "global.h"

void sub_0801C2B8(u8);
void sub_0801C184(void);
void sub_0801C1D4(void);
void sub_08007404(void);
void sub_08021E50(u32);
void sub_0801E5C8(void);
void sub_0801CE4C(u8);
void sub_0801CF94(u16);
void sub_0801DF38(void);
void sub_0801E138(void);
void sub_0801E564(void);
void sub_0801E3D0(void);
void sub_0801C6D0(void);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_0801E988(void);

extern s8 gUnk_020214D0[];
extern u8 gUnk_02020B20[];
extern u8 gUnk_02021140[];

void sub_0801E82C(void)
{
    u16 card;
    u16 *dst;

    gUnk_020214D0[0x7E9] = gUnk_020214D0[0x7EA];
    sub_0801C2B8(((u8 *)gUnk_020214D0)[0x7E9]);
    sub_0801C184();
    sub_0801C1D4();
    card = **(u16 **)((u32)gUnk_020214D0 +
                      (gUnk_020214D0[0x7E6] + gUnk_020214D0[0x7E7] * 7) * 4);
    dst = (u16 *)gUnk_02020B20;
    dst[8] = card;
    *((u8 *)dst + 0x12) = gUnk_02021140[card];
    sub_08007404();
    sub_08021E50(0x37);
    sub_0801E5C8();
    sub_0801CE4C(((u8 *)gUnk_020214D0)[0x7E9]);
    sub_0801CF94(card);
    sub_0801DF38();
    sub_0801E138();
    sub_0801E564();
    sub_0801E3D0();
    sub_0801C6D0();
    sub_08003B58((void *)0x0801EA39);
    sub_08003BC4();
    sub_0801E988();
}
