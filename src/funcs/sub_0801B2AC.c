#include "global.h"

void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_08021E50(u16);
void sub_0801C324(void);
void sub_0801E4CC(void);
void sub_0801E434(void);

void sub_0801B2AC(void)
{
    sub_0801C324();
    sub_0801E4CC();
    sub_0801E434();
    sub_08003B58((void *)0x0801EB65);
    sub_08003BC4();
    sub_08021E50(0x36);
}
