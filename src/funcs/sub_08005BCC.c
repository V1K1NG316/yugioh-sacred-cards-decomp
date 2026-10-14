#include "global.h"

void sub_080058AC(u8);
void sub_08005D2C(void);
void sub_08021E50(u32);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_08028530(void);

extern u8 gUnk_0201FCC0[];
extern u8 gUnk_08D30F04[];

typedef struct {
    u16 f0;
    u8 f2;
    u8 pad;
    u8 f4;
} T;

void sub_08005BCC(void)
{
    T *s = (T *)0x0201FCC0;

    s->f4 = gUnk_08D30F04[s->f4];
    if ((u8)s->f4 <= 8)
        sub_080058AC(s->f4);
    else
        sub_080058AC(s->f2);

    sub_08005D2C();
    sub_08021E50(0x36);
    sub_08003B58((void *)0x080284CD);
    sub_08003BC4();
    sub_08028530();
}
