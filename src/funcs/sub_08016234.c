#include "global.h"

extern u8 gUnk_02020D30[];

void sub_08016254(void);
void sub_08016360(void);

void sub_08016234(void)
{
    if (gUnk_02020D30[0x29] == 1)
        sub_08016254();
    else
        sub_08016360();
}
