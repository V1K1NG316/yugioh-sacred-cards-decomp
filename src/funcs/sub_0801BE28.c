#include "global.h"

void sub_08006BE4(u16);
void sub_08021E50(u32);
void sub_08015DD8(void);
void sub_08007404(void);
void sub_0801E5E8(void);
void sub_0801C5E4(void);
void sub_0801CC40(void);
void sub_0801CF94(u16);
void sub_0801DED0(void);
void sub_0801E15C(void);
void sub_0801E1C4(void);
void sub_0801E138(void);
void sub_0801E2E4(void);
void sub_0801C67C(void);
void sub_0801E4CC(void);
void sub_0801E434(void);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_0801ED54(void);

extern s8 gUnk_020214D0[];
extern u8 gUnk_02020B20[];
extern u8 gUnk_02021140[];

void sub_0801BE28(void)
{
    u16 card = **(u16 **)((u32)gUnk_020214D0 +
                          (gUnk_020214D0[0x7E6] + gUnk_020214D0[0x7E7] * 7) * 4);
    u16 *dst;

    sub_08006BE4(card);
    sub_08021E50(0x37);
    sub_08015DD8();
    dst = (u16 *)gUnk_02020B20;
    dst[8] = card;
    *((u8 *)dst + 0x12) = gUnk_02021140[card];
    sub_08007404();
    sub_0801E5E8();
    sub_0801C5E4();
    sub_0801CC40();
    sub_0801CF94(card);
    sub_0801DED0();
    sub_0801E15C();
    sub_0801E1C4();
    sub_0801E138();
    sub_0801E2E4();
    sub_0801C67C();
    sub_0801E4CC();
    sub_0801E434();
    sub_08003B58((void *)0x0801EDC9);
    sub_08003BC4();
    sub_08003B58((void *)0x0801ED89);
    sub_08003BC4();
    sub_0801ED54();
}
