#include "global.h"

void sub_08018960(void);
void sub_08018CBC(void);
void sub_08018C0C(void);
void sub_08018A88(void);
void sub_080189A0(void);
void sub_08018D00(void);
void sub_08003B58(void *);
void sub_08003BC4(void);
void sub_08018D24(void);
void sub_08018CE8(void);

void sub_080184AC(void)
{
    sub_08018960();
    sub_08018CBC();
    sub_08018C0C();
    sub_08018A88();
    sub_080189A0();
    sub_08003B58((void *)sub_08018D24);
    sub_08003BC4();
    sub_08018D00();
    sub_08003B58((void *)sub_08018CE8);
    sub_08003BC4();
}
