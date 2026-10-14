#include "global.h"

u8 sub_08014474(void);
void sub_08015208(void);
void sub_080152CC(void);
void sub_0801542C(void);
void sub_08015638(void);

void sub_080151D0(void)
{
    switch (sub_08014474()) {
    case 1:
        sub_080152CC();
        break;
    case 2:
        sub_0801542C();
        break;
    case 3:
        sub_08015638();
        break;
    case 0:
    default:
        sub_08015208();
        break;
    }
}
