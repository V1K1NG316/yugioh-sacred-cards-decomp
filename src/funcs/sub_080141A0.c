#include "global.h"

void sub_0801421C(u32);
void sub_0801425C(u32);
void sub_08014294(void);
void sub_080142B8(void);
void sub_080143E8(void);
void sub_080143EC(void);
void sub_08014424(void);

void sub_080141A0(u32 action)
{
    switch ((u8)action) {
    case 0:
        sub_08014424();
        break;
    case 1:
        sub_080143EC();
        break;
    case 2:
        sub_0801421C(1);
        break;
    case 3:
        sub_0801425C(1);
        break;
    case 4:
        sub_0801421C(0xA);
        break;
    case 5:
        sub_0801425C(0xA);
        break;
    case 6:
        sub_08014294();
        break;
    case 7:
        sub_080142B8();
        break;
    case 8:
        sub_080143E8();
        break;
    }
}
