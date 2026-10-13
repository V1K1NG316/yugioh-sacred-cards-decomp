#include "global.h"

void sub_08028438(void);
void sub_08001410(void);

void sub_080013F4(void)
{
    *(u16 *)0x04000000 = 0x1E00;
    sub_08028438();
    sub_08001410();
}
