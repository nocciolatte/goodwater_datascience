#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def pct_change(orig_val, new_val):
    if not orig_val:
        return 0
    return (new_val - orig_val) / (1.0 * orig_val)

def clv(aov, txn, m1_ret, m3_ret, m12_ret):
    if not aov:
        return 0
    if not txn:
        txn = 1
    if not m1_ret and not m3_ret and not m12_ret:
        return aov * txn
    # modified CLV calculation, assume discount rate = 0.1
    discount_rate = 0.1
    monthly_discount = (1 + discount_rate) ** (1/12.0) - 1

    if m1_ret and m3_ret and m12_ret:
        pv = (aov * txn) / ((1 + monthly_discount) ** 1) + \
             (aov * txn) / ((1 + monthly_discount) ** 3) + \
             (aov * txn) / ((1 + monthly_discount) ** 12)
    elif m1_ret and m3_ret and not m12_ret:
        pv = (aov * txn) / ((1 + monthly_discount) ** 1) + \
             (aov * txn) / ((1 + monthly_discount) ** 3)
    elif m1_ret and not m3_ret and m12_ret:
        pv = (aov * txn) / ((1 + monthly_discount) ** 1) + \
             (aov * txn) / ((1 + monthly_discount) ** 12)
    elif m1_ret and not m3_ret and not m12_ret:
        pv = (aov * txn) / ((1 + monthly_discount) ** 1)
    elif not m1_ret and m3_ret and m12_ret:
        pv = (aov * txn) / ((1 + monthly_discount) ** 3) + \
             (aov * txn) / ((1 + monthly_discount) ** 12)
    elif not m1_ret and m3_ret and not m12_ret:
        pv = (aov * txn) / ((1 + monthly_discount) ** 3)
    elif not m1_ret and not m3_ret and m12_ret:
        pv = (aov * txn) / ((1 + monthly_discount) ** 12)


    return pv + aov * txn



def calculateMetrics(df, feature_name):
    mean = df[feature_name].mean()
    std = df[feature_name].std()
    one_std_lower = mean - std
    one_std_upper = mean + std
    two_std_lower = mean - 2 * std
    two_std_upper = mean + 2 * std

    return mean, std, one_std_lower, one_std_upper, two_std_lower, two_std_upper


def printMetrics(df, feature_name, feature_name_descriptive):
    mean, std, one_std_lower, one_std_upper, two_std_lower, \
        two_std_upper = calculateMetrics(df, feature_name)

    print("$%20s Mean: %10.2f || 1std [%5.2f, %5.2f] || 2std [%5.2f, %5.2f]" % (feature_name_descriptive, mean, one_std_lower,
               one_std_upper, two_std_lower, two_std_upper))
