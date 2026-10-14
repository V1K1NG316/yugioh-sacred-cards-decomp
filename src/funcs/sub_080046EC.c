#include "global.h"

u8 sub_0801457C(u16);

extern u8 gUnk_020203E0[];
extern u8 gUnk_02020770[];
extern u16 gUnk_0201FCCC[];

struct Head
{
    u16 a;
    u8 b;
    u8 c;
};

void sub_080046EC(void)
{
    struct Head *h = (struct Head *)0x0201FCC0;
    u16 i;

    h->a = 0;
    h->c = 1;
    h->b = 0;
    for (i = 0; i <= 0x384; i++)
        gUnk_020203E0[i] = gUnk_02020770[i] + sub_0801457C(i);
    for (i = 0; i <= 0x383; i++)
        gUnk_0201FCCC[i] = i + 1;
}
