#include "global.h"

void sub_080043D0(void);
void sub_080046EC(void);
void sub_080044CC(void);
void sub_080044A4(void);
void sub_08004528(void);
void sub_080044FC(void);
void sub_080046C8(void);
void sub_08004558(void);
void sub_080045E4(void);
void sub_08004630(void);
void sub_080046C4(void);

void sub_0800441C(u8 action)
{
    switch (action) {
    case 0:
        sub_080043D0();
        break;
    case 1:
        sub_080046EC();
        break;
    case 3:
        sub_080044A4();
        break;
    case 2:
        sub_080044CC();
        break;
    case 4:
        sub_08004528();
        break;
    case 5:
        sub_080044FC();
        break;
    case 6:
        sub_080046C8();
        break;
    case 7:
        sub_08004558();
        break;
    case 8:
        sub_080045E4();
        break;
    case 10:
        sub_08004630();
        break;
    case 9:
        sub_080046C4();
        break;
    }
}
