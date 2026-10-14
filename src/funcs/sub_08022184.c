#include "global.h"

u8 sub_08006068(void);
void sub_080060EC(u8);
void sub_080061C8(void);
void sub_0800627C(void);
u8 sub_080221C0(void);
u8 sub_0802222C(void);
void sub_0802240C(void);

void sub_08022184(void)
{
    u8 v;

    if (sub_08006068() == 0)
        v = sub_080221C0();
    else
        v = sub_0802222C();
    if (v == 0)
        sub_0800627C();
    else {
        sub_080060EC(sub_08006068());
        sub_080061C8();
    }
    sub_0802240C();
}
