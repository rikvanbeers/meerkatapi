from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .apps import RankcalcConfig
from rest_framework.permissions import IsAuthenticatedOrReadOnly
import numpy as np


class RankResults(generics.ListAPIView):

    """
    Project Meerkat API - Load Health Comparisson results
    """
    permission_classes = [IsAuthenticatedOrReadOnly]


    def get(self, request, **kwargs):

        # Step 1 - Determine all data needed
        catDim = ["Inpatient Cover", "Orthopaedic", "Day to Day/Outpatient",
                   "Maternity, Fertility & Child Health Benefits", "Outpatient Radiology Benefits", "Overseas Benefits"]

        labelCat      = RankcalcConfig.labelCat
        weightBenefit = RankcalcConfig.weightBenefit
        weightCat     = RankcalcConfig.weightCat
        rankResults   = RankcalcConfig.rankResults
        totalScores   = RankcalcConfig.totalScores

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

        inputPlans    = urlparams["InputPlans"]         # Number of prespecified plans in comparison
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

        if usertoken not in userTokens:
            return Response("User Not Identified", status=status.HTTP_201_CREATED)

        else:

            for key in urlparams:
                keys.append(key)
                userinput.append(urlparams[key])

            inputData    = np.array(userinput)
            inputUser    = inputData[16:len(inputData)].astype(int)

            # Step 1 - Calculate detailed scores per plan
            rankResultsInput = rankResults[1:rankResults.shape[0], :].astype(float)
            finalWeightsDetailed = np.transpose(inputUser) * weightBenefit
            detailedPlanScores = np.transpose(finalWeightsDetailed * np.transpose(rankResultsInput))

            # Step 2 - Calculate scores per benefit category and plan
            rankResultsInput = rankResults[1:rankResults.shape[0], :].astype(float)
            finalWeights = np.transpose(inputUser) * weightBenefit * weightCat
            planStart = 0

            for idx in range(0, len(catDim)):
                planEnd = planStart + sum(1 for x in labelCat if (x == catDim[idx]))
                planScores = np.transpose(finalWeights[planStart:planEnd]) @ rankResultsInput[planStart:planEnd, :]
                totalScores = np.vstack([totalScores, planScores])
                planStart = planEnd


            # Step 3 - Calculate results based on selection
            sumScores = np.transpose(np.ones(totalScores.shape[0] - 1, dtype=int)) @ totalScores[1:totalScores.shape[0], :]

            # Construct selection matrix for filtering
            listPlans = [currentPlan, altPlan1, altPlan2, altPlan3]
            totResults = np.arange(start=0, stop=totalScores.shape[1], step=1)
            totResults = np.vstack([totResults, provNames, sumScores, totalScores[1, :], priceList[:, prefPrice],
                                        np.transpose(inputCovers), totalScores[1:totalScores.shape[0], :], detailedPlanScores])

            # Apply filters to scores
            prefResults = totResults[:, listPlans[0:inputPlans]]
            print(prefResults)
            print(listPlans)
            totResults = np.delete(totResults, listPlans[0:inputPlans], 1)                   # delete plans selected in comparison
            totResults = np.delete(totResults, np.where(totResults[4, :] >= maxPrice), 1)    # delete plans price exceeding max
            totResults = np.delete(totResults, np.where(totResults[5, :] < excessCover), 1)  # delete plans based on excess cover
            totResults = np.delete(totResults, np.where(totResults[6, :] > excessValue), 1)  # delete plans based on excess value
            totResults = np.delete(totResults, np.where(totResults[7, :] < ophthCover),  1)  # delete plans based on ophthalmic

            if prefProvider != "All":
                print(prefProvider)
                totResults = np.delete(totResults, np.where(totResults[1, :] != prefProvider), 1)  # delete plans <> preferred prov

            # Calculate final scores and rank plans
            totSelect = totResults.shape[1]
            maxList = min(5, totSelect)

            intermediateScores = 10 * totResults[2, :] / max(totResults[2, :])
            sortList = np.argpartition(intermediateScores, -maxList)[-maxList:]

            # Add back in the results of the preferred plans specified in the API call
            totResults = np.hstack([totResults, prefResults])


            # Determine outputs
            outputPlanList = np.arange(start=0, stop=4, step=1) + (totSelect - 1)
            outputPlanList = np.hstack([outputPlanList, np.flip(sortList, 0)])
            print(outputPlanList)

            if outputType == 1:             # Calculate score per plan and per benefit
                benefitScores = 10 * totResults[8 + 6 + outputBen, :] / max(totResults[8 + 6 + outputBen, :])
                output = benefitScores[outputPlanList[outputPlan]]

            elif outputType == 2:           # Calculate score per plan and per benefit category
                categoryScores = 10 * totResults[8 + outputBen, :] / max(totResults[8 + outputCat, :])
                output = categoryScores[outputPlanList[outputPlan]]

            elif outputType == 3:           # Calculate price for the plan
                output = priceList[outputPlanList[outputPlan], prefPrice]

            elif outputType == 4:           # Calculate score on total basis
                finalTotalScores = 10 * totResults[2, :] / max(totResults[2, :])
                output = finalTotalScores[outputPlanList[outputPlan]]

            elif outputType == 5:           # Calculate score for Excess amount
                finalExcessScores = 10 * totResults[3, :] / max(totResults[3, :])
                output = finalExcessScores[outputPlanList[outputPlan]]

            else:                           # Calculate output plan number
                output = totResults[0,outputPlanList[outputPlan]]

            return Response(output, status=status.HTTP_201_CREATED)

