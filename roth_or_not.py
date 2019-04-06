import argparse
import numpy as np

RET_MAX_ANN_CONTRIB = 19000
TAX_BRACKETS = [(500000, 0.37, 150690), (200000, 0.35, 45690), (157500, 0.32, 32090),
                (82500, 0.24, 14090), (38700, 0.22, 4454), (9525, 0.12, 953), (0, 0.1, 0)]


def calculate_effective_tax_rate(income):
    for min_amount, marginal_rate, prev_rate_tax in TAX_BRACKETS:
        if income > min_amount:
            tax = prev_rate_tax + (income - min_amount) * marginal_rate
            return tax / income


def investment_account(curr_age, ret_age=67,
                       ann_contrib_posttax=10000, ann_return=0.05, cap_gains=0.15):

    n_years = ret_age - curr_age
    investment_size = n_years * ann_contrib_posttax
    ret_amount_pretax = np.sum((1 + ann_return) ** np.arange(n_years)) * ann_contrib_posttax
    ret_amount_posttax = investment_size + (ret_amount_pretax - investment_size) * (1 - cap_gains)
    return ret_amount_posttax


def roth(curr_age, ret_age=67, ann_contrib_posttax=RET_MAX_ANN_CONTRIB, ann_return=0.05):
    if ann_contrib_posttax > RET_MAX_ANN_CONTRIB:
        non_401k_contrib = ann_contrib_posttax - RET_MAX_ANN_CONTRIB
        roth_return = roth(curr_age, ret_age=ret_age, ann_return=ann_return)
        personal_account_return = investment_account(curr_age, ret_age=ret_age,
                                                     ann_contrib_posttax=non_401k_contrib,
                                                     ann_return=ann_return)
        return roth_return + personal_account_return
    else:
        n_years = ret_age - curr_age
        ret_amount = np.sum((1 + ann_return) ** np.arange(n_years)) * ann_contrib_posttax
        return ret_amount


def pretax(curr_tax_rate, curr_age, ret_age=67, ret_income=80000,
           ann_contrib_posttax=RET_MAX_ANN_CONTRIB, ann_return=0.05):

    ann_contrib_pretax = ann_contrib_posttax / (1 - curr_tax_rate)
    if ann_contrib_pretax > RET_MAX_ANN_CONTRIB:
        non_401k_contrib = (ann_contrib_pretax - RET_MAX_ANN_CONTRIB) * (1 - curr_tax_rate)
        ret_return = pretax(curr_tax_rate, curr_age, ret_age=ret_age, ret_income=ret_income,
                            ann_contrib_posttax=RET_MAX_ANN_CONTRIB * (1 - curr_tax_rate),
                            ann_return=ann_return)
        personal_account_return = investment_account(curr_age, ret_age=ret_age,
                                                     ann_contrib_posttax=non_401k_contrib,
                                                     ann_return=ann_return)
        return ret_return + personal_account_return
    else:
        n_years = ret_age - curr_age
        ret_amount_pretax = np.sum((1 + ann_return) ** np.arange(n_years)) * ann_contrib_pretax
        annual_distribution = ret_amount_pretax / 27.4
        ret_income = max(ret_income, annual_distribution)
        ret_tax_rate = calculate_effective_tax_rate(ret_income)
        ret_amount_posttax = ret_amount_pretax * (1 - ret_tax_rate)
        return ret_amount_posttax


def main(args):
    curr_tax_rate = calculate_effective_tax_rate(args.income)

    roth_return = roth(curr_age=args.current_age, ret_age=args.retirement_age,
                       ann_contrib_posttax=args.annual_contribution,
                       ann_return=args.annual_returns)

    pretax_return = pretax(curr_tax_rate=curr_tax_rate,
                           curr_age=args.current_age, ret_age=args.retirement_age,
                           ret_income=args.expected_retirement_income,
                           ann_contrib_posttax=args.annual_contribution,
                           ann_return=args.annual_returns)
    print('Roth return: ' + str(roth_return))
    print('Pretax return: ' + str(pretax_return))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--income', type=float)
    parser.add_argument('--current-age', type=int)
    parser.add_argument('--retirement-age', type=int, default=67)
    parser.add_argument('--expected-retirement-income', type=float, default=80000)
    parser.add_argument('--annual-contribution', type=float, default=RET_MAX_ANN_CONTRIB)
    parser.add_argument('--annual-returns', type=float, default=0.05)

    args = parser.parse_args()
    main(args)
