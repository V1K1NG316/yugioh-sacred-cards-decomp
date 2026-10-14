#include "global.h"

void sub_08003BC4(void);

void sub_08035AE4(s32 n)
{
    s32 i;

    if (n > 0)
    {
        i = n;
        do
        {
            sub_08003BC4();
        } while (--i != 0);
    }
}
