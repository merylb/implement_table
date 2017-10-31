from implement_table.core import settings
from implement_table.shared.models import Currency
from num2words import num2words
from enum import Enum


class AnswerType(Enum):
    request_deposit = 'request_deposit'
    agreement_reserved = 'agreement_reserved'
    final_agreement_progress = 'final_agreement_progress'
    final_agreement = 'final_agreement'
    rejected = 'rejected'
    information_complement_request = 'information_complement_request'


class PaymentStatus(Enum):
    is_unpaid = 'unpaid'
    is_paid = 'paid'
    is_partial_paid = 'partial'
    is_exempt = 'exempt'


def get_default_currency():
    obj = Currency.objects(is_deleted=False, is_default=True)
    if len(obj) > 0:
        return Currency.objects(is_deleted=False, is_default=True)[0]
    else:
        return None


def amount_to_text(total):
    default_currency = get_default_currency()
    c_full_name = default_currency.full_name if default_currency is not None else ''
    c_fraction_link_word = default_currency.fraction_link_word if default_currency is not None else ''
    c_fraction_name = default_currency.fraction_name if default_currency is not None else ''

    nums = ("%.2f" % total).split('.')
    print('test----------', nums[0])
    whole = num2words(int(nums[0]), lang=settings.LANGUAGE_CODE) + ' ' + c_full_name + '(s)'
    if len(nums) == 2 and int(nums[1]) > 0:
        fraction = num2words(int(nums[1]), lang=settings.LANGUAGE_CODE)
        return whole + c_fraction_link_word + fraction + ' ' + c_fraction_name + '(s)'
    else:
        return whole
