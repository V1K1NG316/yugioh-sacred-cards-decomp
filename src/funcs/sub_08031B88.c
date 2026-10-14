#include "global.h"

void sub_08031D58(void);
void sub_08031BA4(u8 *);

void sub_08031B88(u16 *p)
{
    if (p[0] == 0) {
        sub_08031D58();
    } else {
        sub_08031BA4((u8 *)p);
    }
}
