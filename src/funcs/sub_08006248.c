#include "global.h"

void sub_080061F4(void);
u32 sub_0800648C(void);
void sub_08006368(void);
void sub_08006188(void);
void sub_080063E0(u16);
void sub_0800634C(void);

void sub_08006248(void)
{
    u16 v;

    sub_080061F4();
    v = sub_0800648C();
    sub_08006368();
    sub_08006188();
    sub_080063E0(v);
    sub_0800634C();
}
