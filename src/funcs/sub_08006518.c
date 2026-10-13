#include "global.h"

u32 sub_0803691C(void);
void sub_08006544(u8);
void sub_080065CC(u8);

void sub_08006518(u8 a)
{
    u8 c = sub_0803691C();

    switch (c) {
    case 0:
        sub_08006544(a);
        break;
    case 1:
        sub_080065CC(a);
        break;
    }
}
