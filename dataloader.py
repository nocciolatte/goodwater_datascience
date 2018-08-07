#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from utilities import *


class BenchmarkData(object):

    def __init__(self, datafile):
        assert datafile
        self.df = pd.read_excel(datafile, sheet_name=0)
        self.df.columns = ['company', 'month', 'sales', 'sales_q_ago',
                      'sales_y_ago', 'aov', 'txns_per_customer',
                      'dollars_per_customer', 'm1_retention', 'm3_retention',
                      'm12_retention']

        self.calculateCLV()
        self.calculateSalesGrowths()
        self.createFeaturesDF()
        self.calculateAndStoreAllMetrics()

    def createFeaturesDF(self):
        self.featuresdf = pd.DataFrame(self.df['company'].drop_duplicates())
        self.featuresdf['clv'] = np.nan
        self.featuresdf['1q_sales_pct_chg'] = np.nan
        self.featuresdf['1y_sales_pct_chg'] = np.nan

        for index, row in self.featuresdf.iterrows():

            self.featuresdf.at[index, 'clv'] = self.df['clv'][self.df['company'] ==
                                        row['company']].mean()
            self.featuresdf.at[index, '1q_sales_pct_chg'] = self.df['1q_sales_pct_chg'][self.df['company'] ==
                                        row['company']].mean()
            self.featuresdf.at[index, '1y_sales_pct_chg'] = self.df['1y_sales_pct_chg'][self.df['company'] ==
                                        row['company']].mean()



    def calculateCLV(self):
        self.df['clv'] = np.vectorize(clv)(self.df['aov'],
                                           self.df['txns_per_customer'],
                                           self.df['m1_retention'],
                                           self.df['m3_retention'],
                                           self.df['m12_retention'])

    def calculateSalesGrowths(self):
        self.df['1q_sales_pct_chg'] = np.vectorize(pct_change)(self.df['sales_q_ago'], self.df['sales'])

        self.df['1y_sales_pct_chg'] = np.vectorize(pct_change)(self.df['sales_y_ago'], self.df['sales'])


    def calculateMetrics(self, df, feature_name):
        mean = df[feature_name].mean()
        std = df[feature_name].std()
        one_std_lower = mean - std
        one_std_upper = mean + std
        two_std_lower = mean - 2 * std
        two_std_upper = mean + 2 * std

        return mean, std, one_std_lower, one_std_upper, two_std_lower, two_std_upper

    def calculateAndStoreAllMetrics(self):
        self.clv_mean, self.clv_std, lower1, upper1, lower2, upper2 = self.calculateMetrics(self.df, 'clv')

        self.qchg_mean, self.qchg_std, lower1, upper1, lower2, upper2 = self.calculateMetrics(self.df, '1q_sales_pct_chg')

        self.ychg_mean, self.ychg_std, lower1, upper1, lower2, upper2 = self.calculateMetrics(self.df, '1y_sales_pct_chg')


    def printMetrics(self, df, feature_name, feature_name_descriptive):
        mean, std, one_std_lower, one_std_upper, two_std_lower, \
            two_std_upper = self.calculateMetrics(df, feature_name)

        print("$%20s Mean: %10.2f || 1std [%5.2f, %5.2f] || 2std [%5.2f, %5.2f]" % (feature_name_descriptive, mean, one_std_lower,
                   one_std_upper, two_std_lower, two_std_upper))

    def printAllMetrics(self):
        printMetrics(self.df, 'clv', "CLV")
        printMetrics(self.df, '1q_sales_pct_chg', "1Q Sales Change")
        printMetrics(self.df, '1y_sales_pct_chg', "1Y Sales Change")



class SampleData(object):
    def __init__(self, datafile):
        assert datafile
        self.df_sales_raw = pd.read_excel(datafile, sheet_name=1)
        self.df_ret_raw = pd.read_excel(datafile, sheet_name=2)

        self.__processRet()
        self.__processSales()
        self.calculateCLV()
        self.calculateSalesGrowths()

    def calculateSalesGrowths(self):
        self.df_sales['1q_sales_pct_chg'] = np.vectorize(pct_change)(self.df_sales['sales_q_ago'],
                                 self.df_sales['sales'])

        self.df_sales['1y_sales_pct_chg'] = np.vectorize(pct_change)(self.df_sales['sales_y_ago'],
                                 self.df_sales['sales'])

    def calculateCLV(self):
        self.df_ret['clv'] = np.vectorize(clv)(self.df_ret['aov'],
                                               self.df_ret['txns_per_customer'],
                                               self.df_ret['m1_retention'],
                                               self.df_ret['m3_retention'],
                                               self.df_ret['m12_retention'])



    def classify(self, benchmark_clv_mean, benchmark_clv_std,
                 benchmark_qchg_mean, benchmark_qchg_std, benchmark_ychg_mean,
                 benchmark_ychg_std):

        self.df_classify = pd.DataFrame(self.df_ret['company'])


        self.df_classify['pass_clv_test'] = (self.df_ret['clv'] >=
                                             benchmark_clv_mean)
        self.df_classify['strong_pass_clv_test'] = (self.df_ret['clv'] >=
                                                    benchmark_clv_mean +
                                                    benchmark_clv_std)

        self.df_classify['pass_q_growth_test'] =    (self.df_sales['1q_sales_pct_chg'] >= benchmark_qchg_mean - benchmark_qchg_std)
        self.df_classify['strong_pass_q_growth_test'] = (self.df_sales['1q_sales_pct_chg'] >= benchmark_qchg_mean)

        self.df_classify['pass_y_growth_test'] =    (self.df_sales['1y_sales_pct_chg'] >= benchmark_ychg_mean - benchmark_ychg_std)
        self.df_classify['strong_pass_y_growth_test'] = (self.df_sales['1y_sales_pct_chg'] >= benchmark_ychg_mean)


    def printClassifyResults(self):
        passed_clv = self.df_classify['company'][self.df_classify['pass_clv_test'] == True]
        strong_passed_clv = self.df_classify['company'][self.df_classify['strong_pass_clv_test'] == True]

        passed_q_growth = self.df_classify['company'][self.df_classify['pass_q_growth_test'] == True]
        strong_passed_q_growth = self.df_classify['company'][self.df_classify['strong_pass_q_growth_test'] == True]

        passed_y_growth = self.df_classify['company'][self.df_classify['pass_y_growth_test'] == True]
        strong_passed_y_growth = self.df_classify['company'][self.df_classify['strong_pass_y_growth_test'] == True]

        passed_all = self.df_classify['company'][(self.df_classify['pass_clv_test'] == True) & (self.df_classify['pass_q_growth_test'] == True) & (self.df_classify['pass_y_growth_test'] == True)]

        print("Passed CLV Test: %s" % (", ".join(str(c) for c in passed_clv)))
        print("Strongly Passed CLV Test: %s" % (",".join(str(c) for c in strong_passed_clv)))
        print('\n')

        print("Passed 1Q Growth Test: %s" % (", ".join(str(c) for c in passed_q_growth)))
        print("Strongly Passed 1Q Growth Test: %s" % (", ".join(str(c) for c in strong_passed_q_growth)))
        print('\n')

        print("Passed 1Y Growth Test: %s" % (", ".join(str(c) for c in passed_y_growth)))
        print("Strongly Passed 1Y Growth Test: %s" % (", ".join(str(c) for c in strong_passed_y_growth)))

        print('\n')
        print("Passed All Tests: %s" % (", ".join(str(c) for c in passed_all)))

    def __processSales(self):

        self.df_sales = pd.DataFrame(self.df_ret_raw['company'].drop_duplicates())
        self.df_sales['sales'] = np.nan
        self.df_sales['sales_q_ago'] = np.nan
        self.df_sales['sales_y_ago'] = np.nan

        for index, row in self.df_sales.iterrows():
            self.df_sales.at[index, 'sales'] = self.df_sales_raw['sales'][(self.df_sales_raw['company'] == row['company']) & (self.df_sales_raw['month'] == '2018-06')]

            self.df_sales.at[index, 'sales_q_ago'] = self.df_sales_raw['sales'][(self.df_sales_raw['company'] == row['company']) & (self.df_sales_raw['month'] == '2018-03')]

            self.df_sales.at[index, 'sales_y_ago'] = self.df_sales_raw['sales'][(self.df_sales_raw['company'] == row['company']) & (self.df_sales_raw['month'] == '2017-06')]


    def __processRet(self):

        self.df_ret = pd.DataFrame(self.df_ret_raw['company'].drop_duplicates())
        self.df_ret['m1_retention'] = np.nan
        self.df_ret['m3_retention'] = np.nan
        self.df_ret['m12_retention'] = np.nan
        self.df_ret['aov'] = np.nan
        self.df_ret['txns_per_customer'] =  np.nan

        for index, row in self.df_ret.iterrows():
            self.df_ret.at[index, 'm1_retention'] = self.df_ret_raw['customer_retention'][(self.df_ret_raw['company'] == row['company']) & (self.df_ret_raw['month_no'] == 1)].mean()

            self.df_ret.at[index, 'm3_retention'] = self.df_ret_raw['customer_retention'][(self.df_ret_raw['company'] == row['company']) & (self.df_ret_raw['month_no'] == 3)].mean()

            self.df_ret.at[index, 'm12_retention'] = self.df_ret_raw['customer_retention'][(self.df_ret_raw['company'] == row['company']) & (self.df_ret_raw['month_no'] == 12)].mean()

            self.df_ret.at[index, 'aov'] = self.df_sales_raw['aov'][self.df_sales_raw['company'] == row['company']].mean()

            self.df_ret.at[index, 'txns_per_customer'] = self.df_sales_raw['txns_per_customer'][self.df_sales_raw['company'] == row['company']].mean()
