#include "global.h"

void sub_080130F0(u8);
void sub_08013330(u8);
void sub_080132D0(void);
void sub_08013404(void);
void sub_080133DC(void);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_08021E50(u32);
void sub_080133E0(void);
void sub_08013410(void);
void sub_08013420(void);

u8 sub_0801331C(void);

void sub_08013090(u8 side)
{
    sub_08013330(side);
    sub_08003B58((void *)sub_080133E0);
    sub_08003BC4();
    sub_08013404();
    sub_08021E50(0x44);
    do {
        sub_080130F0(side);
        sub_08003B58((void *)sub_08013410);
        sub_08003BC4();
        sub_080132D0();
    } while (sub_0801331C() != 0);
    sub_080133DC();
    sub_08003B58((void *)sub_08013420);
    sub_08003BC4();
}
