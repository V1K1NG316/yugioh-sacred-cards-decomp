#include "global.h"

void sub_08022FAC(void);
void sub_08028018(void);
void sub_08028090(void);
void sub_08028214(void);
void sub_08003B58(void *);
void sub_08003BC4(void);

void sub_08027FE4(void)
{
    sub_08022FAC();
    sub_08028018();
    sub_08028090();
    sub_08003B58((void *)0x080285D9);
    sub_08003BC4();
    sub_08028214();
    sub_08003B58((void *)0x08028231);
    sub_08003BC4();
}
