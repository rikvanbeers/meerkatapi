from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .apps import RankcalcConfig
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import numpy as np


class DescrResults(generics.ListAPIView):

    """
    Project Meerkat API - Load plan descriptions
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, **kwargs):

        # Step 1 - Determine all data needed

        descrList = RankcalcConfig.descrList


        # Step 2 - Read in user input
        urlparams = self.kwargs

        usertoken = urlparams["userToken"]    # User token specified
        outputPlan = urlparams["OutputPlan"]  # Output plan number
        outputBen = urlparams["OutputBen"]    # Output benefit

        # Step 3 - Determine output

        output = descrList[outputBen - 1, outputPlan]
        return Response(output, status=status.HTTP_201_CREATED)


class RankResults(generics.ListAPIView):

    """
    Project Meerkat API - Load Health Comparisson results
    """
    permission_classes = [IsAuthenticatedOrReadOnly]


    def get(self, request, **kwargs):

        # Step 1 - Determine all data needed

        labelCat      = RankcalcConfig.labelCat
        weightBenefit = RankcalcConfig.weightBenefit
        weightCat     = RankcalcConfig.weightCat
        rankResults   = RankcalcConfig.rankResults
        catScores     = RankcalcConfig.catScores

        provNames     = RankcalcConfig.provNames
        priceList     = RankcalcConfig.priceList
        inputCovers   = RankcalcConfig.inputCovers

        userTokens    = RankcalcConfig.userTokens

        # Step 2 - Read in user input
        keys = []
        userinput = []

        urlparams = self.kwargs

        usertoken     = urlparams["userToken"]          # User token specified
        outputPlan    = urlparams["OutputPlan"]         # 1 = Current, 2 = Alt1, 3 = Alt2, 4 = Alt3, 5 to 9 = Top #5
        outputType    = urlparams["OutputType"]         # Output type required
        outputBen     = urlparams["OutputBen"]          # Output benefit
        outputCat     = urlparams["OutputCat"]          # OUtput category

        currentPlan   = urlparams["CurrentPlan"]        # Current plan specified in comparison
        altPlan1      = urlparams["AltPlan1"]           # Prespecified alternative plan 1
        altPlan2      = urlparams["AltPlan2"]           # Prespecified alternative plan 2
        altPlan3      = urlparams["AltPlan3"]           # Prespecified alternative plan 3

        prefProvider  = urlparams["PrefProvider"]       # Irish Life, Laya, VHI, All
        prefPrice     = urlparams["PrefPrice"]          # 1=adult,2=young adult,3=child
        maxPrice      = urlparams["MaxPrice"]           # maximum price in selection
        excessCover   = urlparams["ExcessCover"]        # 0 = does not matter, 1 = should be included
        excessValue   = urlparams["ExcessValue"]        # maximum value Excess allowed
        ophthCover    = urlparams["OphthCover"]         # 0 = does not matter, 1 = should be included
        ortScore      = urlparams["OrtScore"]           # Orthopaedic category score - vaues are {1,2,3,4,5}

        if usertoken not in userTokens:
            return Response("User Not Identified", status=status.HTTP_201_CREATED)

        else:

            catDim = ["Inpatient Cover", "Orthopaedic", "Day to Day/Outpatient",
                      "Maternity, Fertility & Child Health Benefits",
                      "Outpatient Radiology Benefits", "Overseas Benefits"]

            for key in urlparams:
                keys.append(key)
                userinput.append(urlparams[key])

            inputData    = np.array(userinput)
            inputUser    = inputData[16:len(inputData)].astype(int) / 10

            # Step 1 - Calculate detailed scores per plan
            rankResultsInput = rankResults[1:rankResults.shape[0], :].astype(float)
            finalWeightsDetailed = np.transpose(inputUser) * weightBenefit
            detailedPlanScores = np.transpose(finalWeightsDetailed * np.transpose(rankResultsInput))

            # Step 2 - Calculate scores per benefit category and plan
            inpatientDim = np.count_nonzero(labelCat == catDim[0])

            if ortScore == 1:
                weightCat[0:inpatientDim] = 5
            elif ortScore == 2:
                weightCat[0:inpatientDim] = 4.25
            else:
                weightCat[0:inpatientDim] = 3.5

            rankResultsInput = rankResults[1:rankResults.shape[0], :].astype(float)
            finalWeights = np.transpose(inputUser) * weightBenefit * weightCat
            planStart = 0

            for idx in range(0, len(catDim)):
                planEnd = planStart + sum(1 for x in labelCat if (x == catDim[idx]))
                planScores = np.transpose(finalWeights[planStart:planEnd]) @ rankResultsInput[planStart:planEnd, :]
                catScores = np.vstack([catScores, planScores])
                planStart = planEnd


            # Step 3 - Calculate scores for all plans, benefits and categories
            sumScores = np.transpose(np.ones(catScores.shape[0] - 1, dtype=int)) @ catScores[1:catScores.shape[0], :]

            if max(sumScores) != 0:
                totalScores = 10 * sumScores / max(sumScores)
            else:
                totalScores = 0 * sumScores

            if max(detailedPlanScores[outputBen - 1, :]) != 0:
                benefitScores  = 10 * detailedPlanScores[outputBen - 1, :] / max(detailedPlanScores[outputBen - 1, :])
            else:
                benefitScores  = 0 * detailedPlanScores[outputBen - 1, :]

            if max(catScores[outputCat, :]) != 0:
                categoryScores = 10 * catScores[outputCat, :] / max(catScores[outputCat, :])
            else:
                categoryScores = 0 * catScores[outputCat, :]

            if max(catScores[1, :]) != 0:
                excessCoverScores = 10 * catScores[1, :] / max(catScores[1, :])
            else:
                excessCoverScores = 0 * catScores[1, :]

            # Step 4 - Filter results
            listPlans = [currentPlan, altPlan1, altPlan2, altPlan3]
            totResults = np.arange(start=0, stop=catScores.shape[1], step=1)
            totResults = np.vstack([totResults, provNames, totalScores, excessCoverScores, priceList[:, prefPrice],
                                        np.transpose(inputCovers), categoryScores, benefitScores])

            for idx in listPlans:
                totResults = np.delete(totResults, np.where(totResults[0, :] == idx -1), 1)  # delete plans already selected

            totResults = np.delete(totResults, np.where(totResults[4, :] >= maxPrice), 1)    # delete plans price exceeding max
            totResults = np.delete(totResults, np.where(totResults[5, :] < excessCover), 1)  # delete plans based on excess cover
            totResults = np.delete(totResults, np.where(totResults[6, :] > excessValue), 1)  # delete plans based on excess value
            totResults = np.delete(totResults, np.where(totResults[7, :] < ophthCover),  1)  # delete plans based on ophthalmic

            if prefProvider != "All":
                totResults = np.delete(totResults, np.where(totResults[1, :] != prefProvider), 1)  # delete plans <> preferred prov

            # Step 5 - Calculate list of alternative plans & full list of plans
            totSelect = totResults.shape[1]
            maxList   = min(5, totSelect)
            sortList  = np.argpartition(totResults[2, :], -maxList)[-maxList:]
            finalList = totResults[0, sortList]

            outputPlanList = np.append(listPlans, np.flip(finalList, 0) + 1)

            # Step 6 - Determine outputs
            if outputType == 1:  # Calculate score per plan and per benefit
                output = benefitScores[outputPlanList[outputPlan - 1] - 1]

            elif outputType == 2:  # Calculate score per plan and per benefit category
                output = categoryScores[outputPlanList[outputPlan - 1] - 1]

            elif outputType == 3:  # Calculate price for the plan
                output = priceList[outputPlanList[outputPlan - 1] - 1, prefPrice]

            elif outputType == 4:  # Calculate score on total basis
                output = totalScores[outputPlanList[outputPlan - 1] - 1]

            elif outputType == 5:  # Calculate score for Excess amount
                output = excessCoverScores[outputPlanList[outputPlan - 1] - 1]

            else:  # Calculate output plan number
                output = outputPlanList[outputPlan - 1]

            return Response(output, status=status.HTTP_201_CREATED)

