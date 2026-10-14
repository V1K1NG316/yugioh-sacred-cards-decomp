#include "global.h"

void sub_08027EEC(void);
void sub_08027EFC(void);
void sub_08027F28(void);
void sub_08027F54(void);

extern u8 gUnk_02023438[];

void sub_08027EB0(void)
{
    switch (gUnk_02023438[4]) {
    case 0:
        sub_08027EEC();
        break;
    case 1:
        sub_08027EFC();
        break;
    case 2:
        sub_08027F28();
        break;
    case 4:
        sub_08027F54();
        break;
    }
}
