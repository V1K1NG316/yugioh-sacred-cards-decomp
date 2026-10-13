#include "global.h"

u8 sub_08006068(void);
void sub_08006220(void);
void sub_08006248(void);

void sub_08006128(void)
{
    switch (sub_08006068()) {
    case 0:
    case 1:
        break;
    case 2:
        sub_08006220();
        break;
    case 3:
        sub_08006248();
        break;
    }
}
