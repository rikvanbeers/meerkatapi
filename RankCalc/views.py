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

        userTokens    = RankcalcConfig.userTokens

        # Step 2 - Read in user input
        keys = []
        userinput = []

        urlparams = self.kwargs

        usertoken     = urlparams["userToken"]
        outputBenCat  = urlparams["OutputBenCat"]
        outputBenPlan = urlparams["OutputBenPlan"]

        if usertoken not in userTokens:
            return Response("User Not Identified", status=status.HTTP_201_CREATED)

        else:

            for key in urlparams:
                keys.append(key)
                userinput.append(urlparams[key])

            inputData    = np.array(userinput)
            inputUser    = inputData[3:len(inputData)].astype(int)

            # Step 3 - Perform calculations
            finalWeights = np.transpose(inputUser) * weightBenefit * weightCat
            planStart = 0

            for idx in range(0, len(catDim)):
                planEnd = planStart + sum(1 for x in labelCat if (x == catDim[idx]))
                planScores = np.transpose(finalWeights[planStart:planEnd]) @ rankResults[planStart:planEnd, :]
                totalScores = np.vstack([totalScores, planScores])
                planStart = planEnd

            #outputDict = dict(enumerate(totalScores[outputChoice].flatten(), 1))
            return Response(totalScores[outputBenCat, outputBenPlan], status=status.HTTP_201_CREATED)

