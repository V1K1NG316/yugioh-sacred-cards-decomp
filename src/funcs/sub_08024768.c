#include "global.h"

void sub_08003B58(void *);
void sub_080248F4(void);
void sub_080257F4(void);
void sub_080274D4(void);
void sub_08028438(void);

void sub_08024768(void)
{
    sub_080257F4();
    *(u16 *)0x04000000 = 0;
    sub_080274D4();
    sub_080248F4();
    sub_08003B58((void *)sub_08028438);
}
