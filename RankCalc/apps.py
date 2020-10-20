from django.apps import AppConfig
import pandas as pd
import os


class RankcalcConfig(AppConfig):
    name = 'RankCalc'
    BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FileFolder = os.path.join(BaseDir, 'staticfiles/inputfiles/')

    inputWeights = "inputweights.csv"
    inputRanks = "inputranks.csv"
    inputTokens = "usertokens.csv"

    dfWeights = pd.read_csv(FileFolder + inputWeights)
    dfRanks = pd.read_csv(FileFolder + inputRanks)
    dfTokens = pd.read_csv(FileFolder + inputTokens)

    # Step 3 - Calculate weights
    labelCat = dfWeights.values[:, 1]
    weightBenefit = dfWeights.values[:, 2]
    weightCat = dfWeights.values[:, 3]
    rankResults = dfRanks.values[:, 1:dfRanks.shape[1]]

    # Step 4 - Calculate final scores per plan
    totalScores = dfRanks.columns.values[1:(dfRanks.shape[1])]

    # Step 5 - Determine user tokens list
    userTokens = dfTokens.values

