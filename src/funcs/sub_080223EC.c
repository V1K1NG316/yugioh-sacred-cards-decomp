#include "global.h"

void sub_08022600(void);
void sub_08022744(void);
void sub_08022774(void);
void sub_080228A4(void);
void sub_08003B58(void *);
void sub_08003BC4(void);

void sub_080223EC(void)
{
    sub_08022600();
    sub_08022744();
    sub_08022774();
    sub_08003B58((void *)sub_080228A4);
    sub_08003BC4();
}
