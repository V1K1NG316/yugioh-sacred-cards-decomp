#include "global.h"

u32 sub_080230E4(void);
void sub_08023160(void);

void sub_080230CC(void)
{
    if ((sub_080230E4() & 0x1F) == 0x1F)
        sub_08023160();
}
