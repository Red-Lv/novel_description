#! /bin/env python
#! -*coding:GBK-*-
#! Usage:
#!      transformation between the half width ascii characters and full width ones
#!      for more detail, we should take the kana into consideration

__author__ = 'lvleibing01'


def halfwidth_to_fullwidth(uni_char):
    """
    """

    if not isinstance(uni_char, unicode):
        print 'the parameter uni_str is not a instance of unicode'
        return None

    if ord(uni_char) == 0x0020:
        return unichr(0x3000)

    if 0x0021 <= ord(uni_char) <= 0x007E:
        return unichr(ord(uni_char) - 0x21 + 0xFF01)

    return uni_char


def fullwidth_to_halfwidth(uni_char):
    """
    """

    if not isinstance(uni_char, unicode):
        print 'the parameter uni_str is not a instance of unicode'
        return None

    if ord(uni_char) == 0x3000:
        return unichr(0x0020)

    if 0xFF01 <= ord(uni_char) <= 0xFF5E:
        return unichr(ord(uni_char) - 0xFF01 + 0x21)

    return uni_char

if __name__ == '__main__':

    a = '1'
    print halfwidth_to_fullwidth(unicode(a))

    b = '！'
    print fullwidth_to_halfwidth(unicode(b, 'GBK'))
