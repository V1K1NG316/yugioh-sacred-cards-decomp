#include "global.h"

void sub_080284CC(void);
void sub_08028438(void);
void sub_080284A0(void);

extern u16 gUnk_02023454[];
extern u16 gUnk_0202346C[];
extern u16 gUnk_02023470[];
extern u16 gUnk_02023460[];
extern u16 gUnk_02023474[];
extern u16 gUnk_02023450[];
extern u16 gUnk_0202344C[];
extern u16 gUnk_02023458[];
extern u16 gUnk_0202345C[];
extern u16 gUnk_02023468[];
extern u16 gUnk_02023464[];

void sub_08028230(void)
{
    sub_080284CC();
    gUnk_02023454[0] = 0;
    gUnk_0202346C[0] = 0;
    gUnk_02023470[0] = 0;
    gUnk_02023460[0] = 0;
    gUnk_02023474[0] = 0;
    gUnk_02023450[0] = 0;
    gUnk_0202344C[0] = 4;
    gUnk_02023458[0] = 0;
    gUnk_0202345C[0] = 0;
    gUnk_02023468[0] = 0;
    gUnk_02023464[0] = 0;
    sub_08028438();
    sub_080284A0();
    *(u16 *)0x0400000E = 0x1F03;
    *(u16 *)0x04000000 = 0x1800;
}
