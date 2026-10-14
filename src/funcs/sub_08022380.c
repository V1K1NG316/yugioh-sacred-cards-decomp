#include "global.h"

void sub_08022500(void);
void sub_08022564(void);

u32 sub_08022380(u8 a)
{
    if (a == 1) {
        a = 0;
        sub_08022564();
    } else {
        a = 1;
        sub_08022500();
    }
    return a;
}
