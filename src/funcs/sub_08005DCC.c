#include "global.h"

void sub_08003B58(void *fn);
void sub_08003BC4(void);

void sub_08005F48(void);
void sub_08005FE0(void);
void sub_08005E80(void);
void sub_08005EAC(void);
void sub_08006044(void);

void sub_08005DCC(u8 action)
{
    switch (action) {
    case 1:
        sub_08003B58((void *)sub_08005F48);
        break;
    case 2:
        sub_08003B58((void *)0x08005FD9);
        break;
    case 3:
        sub_08003B58((void *)sub_08005FE0);
        break;
    case 4:
        sub_08003B58((void *)0x08006009);
        break;
    case 6:
        sub_08003B58((void *)0x08006029);
        break;
    case 5:
        sub_08003B58((void *)0x0800603D);
        break;
    case 7:
        sub_08003B58((void *)sub_08005E80);
        break;
    case 8:
        sub_08003B58((void *)sub_08005EAC);
        break;
    case 9:
        sub_08003B58((void *)sub_08006044);
        break;
    }

    sub_08003BC4();
}
