from django.urls import path
from RankCalc import views as views

urlpatterns = [
   path('rankresults/<str:userToken>&<int:OutputType>&<int:OutputPlan>&<int:OutputBen>&<int:OutputCat>&'
        '<int:CurrentPlan>&<int:AltPlan1>&<int:AltPlan2>&<int:AltPlan3>&<str:PrefProvider>&<int:PrefPrice>&'
        '<int:MaxPrice>&<int:ExcessCover>&<int:ExcessValue>&<int:OphthCover>&<int:OrtScore>&'
        '<int:Ben1>&<int:Ben2>&<int:Ben3>&<int:Ben4>&<int:Ben5>&<int:Ben6>&<int:Ben7>&<int:Ben8>&'
        '<int:Ben9>&<int:Ben10>&<int:Ben11>&<int:Ben12>&<int:Ben13>&<int:Ben14>&<int:Ben15>&<int:Ben16>&<int:Ben17>&'
        '<int:Ben18>&<int:Ben19>&<int:Ben20>&<int:Ben21>&<int:Ben22>&<int:Ben23>&<int:Ben24>&<int:Ben25>&<int:Ben26>&'
        '<int:Ben27>&<int:Ben28>&<int:Ben29>&<int:Ben30>&<int:Ben31>&<int:Ben32>&<int:Ben33>&<int:Ben34>&<int:Ben35>&'
        '<int:Ben36>&<int:Ben37>&<int:Ben38>&<int:Ben39>&<int:Ben40>&<int:Ben41>&<int:Ben42>&<int:Ben43>&<int:Ben44>&'
        '<int:Ben45>&<int:Ben46>&<int:Ben47>&<int:Ben48>&<int:Ben49>&<int:Ben50>&<int:Ben51>&<int:Ben52>&<int:Ben53>&'
        '<int:Ben54>&<int:Ben55>&<int:Ben56>&<int:Ben57>&<int:Ben58>&<int:Ben59>&<int:Ben60>&<int:Ben61>&<int:Ben62>&'
        '<int:Ben63>&<int:Ben64>&<int:Ben65>&<int:Ben66>&<int:Ben67>&<int:Ben68>&<int:Ben69>&<int:Ben70>&<int:Ben71>&'
        '<int:Ben72>&<int:Ben73>&<int:Ben74>&<int:Ben75>', views.RankResults.as_view(), name='rankresults'),

   path('descriptions/<str:userToken>&<int:OutputPlan>&<int:OutputBen>',
        views.DescrResults.as_view(), name='descrresults'),
]