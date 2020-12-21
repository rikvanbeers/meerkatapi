from django.apps import AppConfig
import pandas as pd
import os


class RankcalcConfig(AppConfig):
    name = 'RankCalc'
    BaseDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    FileFolder = os.path.join(BaseDir, 'staticfiles/inputfiles/')

    inputWeights = "inputweights.csv"
    inputRanks   = "inputranks.csv"
    inputDescr   = "inputdescr.csv"
    inputCovers  = "inputcovers.csv"
    inputPrices  = "inputprices.csv"
    inputTokens  = "usertokens.csv"

    dfWeights = pd.read_csv(FileFolder + inputWeights)
    dfRanks = pd.read_csv(FileFolder + inputRanks)
    dfDescr = pd.read_csv(FileFolder + inputDescr)
    dfCovers = pd.read_csv(FileFolder + inputCovers)
    dfPrices = pd.read_csv(FileFolder + inputPrices)
    dfTokens = pd.read_csv(FileFolder + inputTokens)

    # Step 3 - Calculate weights
    labelCat = dfWeights.values[:, 1]
    weightBenefit = dfWeights.values[:, 2]
    weightCat = dfWeights.values[:, 3]
    rankResults = dfRanks.values[:, 1:dfRanks.shape[1]]

    # Step 4 - Other inputs
    provNames = dfRanks.values[0, 1:dfRanks.shape[1]]                    # load list of provider names
    priceList = dfPrices.values                                          # load prices based on price selection input
    inputCovers = dfCovers.values[:, 1:dfCovers.shape[1]].astype(float)  # load all excess / ophthalmic cover input

    descrList = dfDescr.values                                           # load all descriptions per plan / benefit

    # Step 5 - Calculate final scores per plan
    catScores = dfRanks.columns.values[1:(dfRanks.shape[1])]

    # Step 5 - Determine user tokens list
    userTokens = dfTokens.values

