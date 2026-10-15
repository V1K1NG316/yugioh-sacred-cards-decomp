#include "global.h"

u32 sub_08016D30(u16 cardId)
{
    u32 r = 0;

    switch (cardId) {
    case 17:
        r = 1;
        break;
    case 18:
        r = 2;
        break;
    case 19:
        r = 4;
        break;
    case 20:
        r = 8;
        break;
    case 21:
        r = 16;
        break;
    }
    return r;
}
