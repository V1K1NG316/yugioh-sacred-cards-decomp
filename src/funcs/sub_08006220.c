#include "global.h"

void sub_080061C8(void);
u32 sub_08006468(void);
void sub_08006384(void);
void sub_080061A8(void);
void sub_080063FC(u16);
void sub_0800634C(void);

void sub_08006220(void)
{
    u16 v;

    sub_080061C8();
    v = sub_08006468();
    sub_08006384();
    sub_080061A8();
    sub_080063FC(v);
    sub_0800634C();
}
