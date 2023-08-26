from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from user.models import Member, CarList
from user.serializers import CarListSerializers, ReportListSerializers
from datetime import timedelta, datetime
import pytz
from haversine import haversine
# Create your views here.

# 데이터 업로드 API
@api_view(['POST'])
def Data(request):
    #UnboundLocalError: local variable 'recent_5min' referenced before assignment 에러발생
    recent_5min=None
    if request.method == 'POST':
        if CarList.objects.filter(CarNum=request.data["CarNum"], ReportStatus='F').exists(): # request된 차 번호와 같은 번호의 미신고된 데이터가 있을 경우
            recent_5min = CarList.objects.filter(CarNum=request.data["CarNum"], ReportStatus='F').order_by('-Date').first()
            if recent_5min and datetime.strptime(request.data["Date"], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)-recent_5min.Date >= timedelta(minutes=5):
                # 해당 미신고된 데이터가 request 시점으로부터 5분 이상의 데이터면 
                
                # 여기에 위도, 경도 비교 기능 작성

                # 전 데이터 위도와 경도
                # center_latitude = recent_5min.Latitude
                # center_longitude = recent_5min.Longitube
                current= (recent_5min.Latitude,recent_5min.Longitube)

                # 새로운 위도와 경도
                # new_latitude = request.data["Latitude"]
                # new_longitude = request.data["Longitube"]
                new = (request.data["Latitude"],request.data["Longitube"])

                # 거리 계산
                #print(haversine(current, new, unit = 'm'))
                if haversine(current, new, unit = 'm')<=1.75: # 오차범위 내의 경우
                    recent_5min.ReportStatus = 'T' 
                    recent_5min.save()
                    data = {
                        'BeforeDate': recent_5min.Date,
                        'AfterDate': request.data["Date"],
                        'CarNum': request.data["CarNum"],
                        'BeforeUniqueNumber': recent_5min.UniqueNumber,
                        'AfterUniqueNumber': request.data["UniqueNumber"]  
                    }
                    serializer = ReportListSerializers(data=data)
                    if serializer.is_valid():
                        serializer.save() # ReportList에 저장
                    else:
                        print(serializer.errors)
                        return JsonResponse({'message': 'ReportListSerializer error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else: # 해당 미신고된 데이터가 request 시점으로부터 5분 이상의 데이터가 아니면
                pass
        else: # request된 차 번호와 같은 번호의 미신고된 데이터가 없을 경우
            pass
        dataset = {}
        for i in request.data:
            dataset[i] = request.data[i]
        if recent_5min!=None and recent_5min.ReportStatus == 'T': # 앞서 정의된 recent_5min가 존재하고 ReportStatus가 T인 경우
            dataset['ReportStatus'] = 'T' 
        serializer = CarListSerializers(data=dataset)
        if serializer.is_valid():
            serializer.save()
        else:
            print(serializer.errors)
            return JsonResponse({'message': 'serializer error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'message':"successfully"}, status=status.HTTP_200_OK)
    return JsonResponse({'message': 'error'}, status=status.HTTP_400_BAD_REQUEST)