#include "global.h"

void sub_08027704(void);
void sub_08027C80(void);
void sub_08027D50(void);
void sub_08027DE4(void);

extern u8 gUnk_02023438[];

void sub_080276C8(void)
{
    switch (gUnk_02023438[4]) {
    case 0:
        sub_08027704();
        break;
    case 1:
        sub_08027C80();
        break;
    case 2:
        sub_08027D50();
        break;
    case 4:
        sub_08027DE4();
        break;
    }
}
