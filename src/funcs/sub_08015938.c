#include "global.h"

void sub_080157B8(u8);
void sub_08015A98(void);
void sub_08021E50(u32);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_08028530(void);

extern u8 gUnk_02020C50[];
extern u8 gUnk_08D35BEC[];

typedef struct {
    u16 f0;
    u8 f2, f3, f4, f5, f6;
    u8 f7;
} T;

void sub_08015938(void)
{
    T *s = (T *)0x02020C50;

    s->f7 = gUnk_08D35BEC[s->f7];
    if ((u8)s->f7 <= 8)
        sub_080157B8(s->f7);
    else
        sub_080157B8(s->f5);

    sub_08015A98();
    sub_08021E50(0x36);
    sub_08003B58((void *)0x080284CD);
    sub_08003BC4();
    sub_08028530();
}
