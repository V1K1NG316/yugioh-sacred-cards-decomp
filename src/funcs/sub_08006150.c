#include "global.h"

void sub_08021F54(void);
void sub_08006368(void);
void sub_08006188(void);
void sub_08006384(void);
void sub_080061A8(void);
void sub_0800634C(void);

u16 sub_08021F28(void);
void sub_080063E0(u16);
void sub_080063FC(u16);

void sub_08006150(void)
{
    u16 v;

    sub_08021F54();
    v = sub_08021F28();
    sub_08006368();
    sub_08006188();
    sub_080063E0(v);
    sub_08006384();
    sub_080061A8();
    sub_080063FC(v);
    sub_0800634C();
}
