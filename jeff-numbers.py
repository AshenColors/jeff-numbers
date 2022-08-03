# Jeff's Numbers dictionary for Plover.
#
# Differences compared to standard numbers:
#
# * E, U or EU reverses the entire number, works on more than two digits
# * DZ will return hundreds of dollars for the last number written.
# * D will always double the last digit. Works on multiple and reversed numbers.
# * Z will always suffix "00"
# * Clock:
#   - K- or -BG will add ':00'
#   - K-G will add ":15"
#   - K-B will add ":30"
#   - K-BG will add ":45"
#   - Using 'S' will add 'a.m.' or '*S' will add 'p.m.'
# * WR or RB for Dollars
# * KR or RG for Percents
#
# * R for roman numerals. Use * for lower case.
# * W or B for ordinal suffixes. (1st, 2nd, 3rd, etc.)
# * G to convert a number to words
# * `*` to add a decimal point after, except when used with 0Z, which will prepend a comma.
import re

LONGEST_KEY = 20
DIGITS = '0123456789'
ENDING_DIGITS_MATCHER = re.compile(r'\d+$')
PERMITTED_NON_DIGIT_STROKES = {
    '#R': True,
    '#R*': True,
    '#-R': True,
    '#*R': True,
    '#W': True,
    '#-B': True,
    '#-G': True,
}
AM_SUFFIX = ' a.m.'
PM_SUFFIX = ' p.m.'

def lookup(key):
    result = ''
    needs_space = False

    for stroke in key:
        if not stroke in PERMITTED_NON_DIGIT_STROKES and not any(c in stroke for c in DIGITS):
            raise KeyError

        if needs_space:
            result += ' '
            needs_space = False

        result += digits(stroke)
        control = ''.join(c for c in stroke if c not in '0123456789#-EU')

        if 'RB' in control:
            control = control.replace('RB', '')
            result = re.sub(r'\d+$', r'$\g<0>', result)
            needs_space = True
        elif 'WR' in control:
            control = control.replace('WR', '')
            result = re.sub(r'\d+$', r'$\g<0>', result)
            needs_space = True
        elif 'KR' in control:
            control = control.replace('KR', '')
            result = re.sub(r'\d+$', r'\g<0>%', result)
            needs_space = True
        elif 'RG' in control:
            control = control.replace('RG', '')
            result = re.sub(r'\d+$', r'\g<0>%', result)
            needs_space = True
        elif 'DZ' in control:
            result = re.sub(r'\d+$', r'$\g<0>00', result)
            needs_space = True
        elif 'K' in control or 'BG' in control:
            if 'K' in control:
                if 'BG' in control:
                    result += ':45'
                elif 'G' in control:
                    result += ':15'
                elif 'B' in control:
                    result += ':30'
                else:
                    result += ':00'
            else:
                result += ':00'

            if 'S' in control:
                if '*' in control:
                    result += AM_SUFFIX
                else:
                    result += PM_SUFFIX

            control = ''.join(c for c in stroke if c not in 'KBGS')
            needs_space = True
        elif 'W' in control or 'B' in control:
            needs_space = True
            control = ''.join(c for c in stroke if c not in 'WB')
            if len(result) >= 1 and result[-1] == '1':
                if len(result) >= 2 and result[-2] == '1':
                    result += 'th'
                else:
                    result += "st"
            elif len(result) >= 1 and result[-1] == '2':
                if len(result) >= 2 and result[-2] == '1':
                    result += 'th'
                else:
                    result += "nd"
            elif len(result) >= 1 and result[-1] == '3':
                if len(result) >= 2 and result[-2] == '1':
                    result += 'th'
                else:
                    result += "rd"
            else:
                result += "th"
        elif 'G' in control:
            match = ENDING_DIGITS_MATCHER.match(result)
            if not match:
                raise KeyError
            control = control.replace('G', '')
            needs_space = True
            words = toWords(match.group(0))
            result = re.sub(r'\d+$', words, result)
        elif 'R' in control:
            match = ENDING_DIGITS_MATCHER.search(result)
            if not match:
                raise KeyError

            value = int(match.group(0))
            if value < 0 or value > 3999:
                raise KeyError

            roman = toRoman(value)

            if '*' in control:
                roman = roman.lower()
            result = ENDING_DIGITS_MATCHER.sub(roman, result)

            control = control.replace('R', '')
            needs_space = True

        control = ''.join(c for c in control if c not in 'DZ*')
        if control != '':
            raise KeyError

    return result


def digits(val):
    result = ''.join(c for c in val if c in DIGITS)
    control = ''.join(c for c in val if c not in DIGITS)

    if val == '0*Z':
        return ',000'

    if result == '':
        return result

    if 'E' in control or 'U' in control:
        control = control.replace('E', '')
        control = control.replace('U', '')
        result = result[::-1]

    if not 'DZ' in control:
        if 'Z' in control:
            control = control.replace('Z', '')
            result += '00'

        if 'D' in control:
            result += result[-1]

    if '*' in control and not 'R' in control and not 'S' in control:
        result += '.'

    return result


ROMAN_VALUES = [
    1000, 900, 500, 400,
    100, 90, 50, 40,
    10, 9, 5, 4,
    1
]
ROMAN_SYMBOLS = [
    "M", "CM", "D", "CD",
    "C", "XC", "L", "XL",
    "X", "IX", "V", "IV",
    "I"
]


def toRoman(num):
    result = ''
    i = 0
    while num > 0:
        for _ in range(num // ROMAN_VALUES[i]):
            result += ROMAN_SYMBOLS[i]
            num -= ROMAN_VALUES[i]
        i += 1
    return result

# ---- Adapted from https://programsolve.com/python-to-convert-numbers-to-words-with-source-code/


ONE_DIGIT_WORDS = {
    '0': ["zero"],
    '1': ["one"],
    '2': ["two", "twen"],
    '3': ["three", "thir"],
    '4': ["four", "for"],
    '5': ["five", "fif"],
    '6': ["six"],
    '7': ["seven"],
    '8': ["eight"],
    '9': ["nine"],
}

TWO_DIGIT_WORDS = ["ten", "eleven", "twelve"]
HUNDRED = "hundred"
LARGE_SUM_WORDS = ["thousand", "million", "billion", "trillion", "quadrillion",
                   "quintillion", "sextillion", "septillion", "octillion", "nonillion"]


def toWords(n):
    word = []

    if len(n) % 3 != 0 and len(n) > 3:
        n = n.zfill(3 * (((len(n)-1) // 3) + 1))

    sum_list = [n[i:i + 3] for i in range(0, len(n), 3)]
    skip = False

    for i, num in enumerate(sum_list):
        if num != '000':
            skip = False

        for _ in range(len(num)):
            num = num.lstrip('0')
            if len(num) == 1:
                if len(word) > 0:
                    if HUNDRED in word[-1] or i == len(sum_list) - 1:
                        word.append("and")
                    elif word[-1] in LARGE_SUM_WORDS:
                        word[-1] = word[-1] + ','
                word.append(ONE_DIGIT_WORDS[num][0])
                num = num[1:]
                break

            if len(num) == 2:
                if num[0] != '0':
                    if len(word) > 0:
                        if HUNDRED in word[-1] or i == len(sum_list) - 1:
                            word.append("and")
                        elif word[-1] in LARGE_SUM_WORDS:
                            word[-1] = word[-1] + ','
                    if num.startswith('1'):
                        if int(num[1]) in range(3):
                            word.append(TWO_DIGIT_WORDS[int(num[1])])
                        else:
                            number = ONE_DIGIT_WORDS[num[1]][1 if int(
                                num[1]) in range(3, 6, 2) else 0]
                            word.append(
                                number + ("teen" if not number[-1] == 't' else "een"))
                    else:
                        word.append(ONE_DIGIT_WORDS[num[0]][1 if int(num[0]) in range(2, 6) else 0] + (
                            "ty" if num[0] != '8' else 'y') + ('-' + ONE_DIGIT_WORDS[num[1]][0] if num[1] != '0' else ""))
                    break
                else:
                    num = num[1:]
                    continue

            if len(num) == 3:
                if num[0] != '0':
                    if len(word) > 0:
                        word[-1] = word[-1] + ','
                    word.append(ONE_DIGIT_WORDS[num[0]][0] + " " + HUNDRED)
                    if num[1:] == '00':
                        break
                num = num[1:]

        if len(sum_list[i:]) > 1 and not skip:
            word.append(LARGE_SUM_WORDS[len(sum_list[i:]) - 2])
            skip = True

    return " ".join(map(str.strip, word))
