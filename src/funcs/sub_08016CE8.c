#include "global.h"

u32 sub_08016D00(void);
void sub_08016D78(void);

void sub_08016CE8(void)
{
    if ((sub_08016D00() & 0x1F) == 0x1F)
        sub_08016D78();
}
