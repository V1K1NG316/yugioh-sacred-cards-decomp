#include "global.h"

void sub_08006220(void);
void sub_08006248(void);
void sub_0800627C(void);

void sub_080060EC(u8 a)
{
    switch (a) {
    case 2:
        sub_08006220();
        break;
    case 3:
        sub_08006248();
        break;
    case 0:
        sub_0800627C();
        break;
    default:
        sub_0800627C();
        break;
    case 1:
        break;
    }
}
