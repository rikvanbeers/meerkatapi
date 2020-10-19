from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .apps import RankcalcConfig
from rest_framework import authentication, permissions
import numpy as np


class RankResults(APIView):

    """
    Project Meerkat API - Load Health Comparisson results
    """

    def post(self, request, format=None):

         # Step 1 - Determine all data needed
        catDim = ["Inpatient Cover", "Orthopaedic", "Day to Day/Outpatient",
                  "Maternity, Fertility & Child Health Benefits", "Outpatient Radiology Benefits", "Overseas Benefits"]

        labelCat = RankcalcConfig.labelCat
        weightBenefit = RankcalcConfig.weightBenefit
        weightCat = RankcalcConfig.weightCat
        rankResults = RankcalcConfig.rankResults
        totalScores = RankcalcConfig.totalScores

        # Step 2 - Read in user input
        data = request.data
        keys = []
        inputData = []

        for key in data:
           keys.append(key)
           inputData.append(data[key])

        inputData = np.array(inputData)
        outputChoice = inputData[0]
        inputUser = inputData[1:len(inputData)]

        # Step 3 - Perform calculations
        finalWeights = np.transpose(inputUser) * weightBenefit * weightCat
        planStart = 0

        for idx in range(0, len(catDim)):
            planEnd = planStart + sum(1 for x in labelCat if (x == catDim[idx]))
            planScores = np.transpose(finalWeights[planStart:planEnd]) @ rankResults[planStart:planEnd, :]
            totalScores = np.vstack([totalScores, planScores])
            planStart = planEnd

        outputDict = dict(enumerate(totalScores[outputChoice].flatten(), 1))
        return Response(outputDict, status=status.HTTP_201_CREATED)


# Steps for publishing
# Add authentication - from tutorial
# Add throtling - from tutorial