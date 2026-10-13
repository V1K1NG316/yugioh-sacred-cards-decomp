#include "global.h"

void sub_08006B08(void);
void sub_08006AA0(void);

void sub_08006A78(u8 a)
{
    if (a == 0 || a == 2)
        sub_08006B08();
    if ((u8)(a - 1) <= 1)
        sub_08006AA0();
}
