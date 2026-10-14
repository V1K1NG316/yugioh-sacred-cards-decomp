#include "global.h"

void sub_0801384C(u8);
void sub_08013978(void);
void sub_080137C4(void);
void sub_08013B14(void);
void sub_08013B18(void);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_08021E50(u32);
void sub_08013B24(void);
void sub_08013B4C(void);
u8 sub_08013828(void);

void sub_0801376C(u8 side)
{
    sub_0801384C(side);
    sub_08003B58((void *)sub_08013B24);
    sub_08003BC4();
    sub_08013B18();
    sub_08021E50(0x45);
    do {
        sub_08013978();
        sub_08003B58((void *)sub_08013B4C);
        sub_08003BC4();
        sub_080137C4();
    } while (sub_08013828() != 0);
    sub_08013B14();
    sub_08003B58((void *)0x08013B5D);
    sub_08003BC4();
}
