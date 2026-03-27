import requests
from django.conf import settings
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Favorite
from .serializers import FavoriteSerializer, FavoriteCreateSerializer

HK_API_URL = 'https://api.data.gov.hk/v1/carpark-info-vacancy'
CACHE_TIMEOUT_INFO = 3600      # 1 hour for static info
CACHE_TIMEOUT_VACANCY = 120    # 2 minutes for real-time vacancy


def _fetch_hk_data(url, cache_key, timeout, params=None):
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        cache.set(cache_key, data, timeout)
        return data
    except Exception:
        return None


def _normalize_carpark_info(raw_carpark):
    return {
        'carparkNo': raw_carpark.get('park_Id', ''),
        'name': raw_carpark.get('name', ''),
        'nameEn': '',
        'districtTc': raw_carpark.get('district', ''),
        'districtEn': '',
        'addressTc': raw_carpark.get('displayAddress', ''),
        'addressEn': '',
        'latitude': raw_carpark.get('latitude'),
        'longitude': raw_carpark.get('longitude'),
        'contactNo': raw_carpark.get('contactNo', ''),
        'website': raw_carpark.get('website', ''),
        'openingHours': raw_carpark.get('opening_status', ''),
        'vehicleTypes': [
            {'vehicleType': key}
            for key in ('privateCar', 'LGV', 'HGV', 'CV', 'coach', 'motorCycle')
            if isinstance(raw_carpark.get(key), dict)
        ],
    }


def _normalize_vacancy_data(raw_entry):
    carpark_id = raw_entry.get('park_Id', '')
    normalized_entries = []

    for vehicle_type in ('privateCar', 'LGV', 'HGV', 'CV', 'coach', 'motorCycle'):
        vehicle_entries = raw_entry.get(vehicle_type)
        if not isinstance(vehicle_entries, list):
            continue

        for item in vehicle_entries:
            normalized_entries.append({
                'carparkNo': carpark_id,
                'vehicleType': vehicle_type,
                'vacancy': item.get('vacancy', 0),
                'vacancyType': item.get('vacancy_type', ''),
                'lastUpdateTime': item.get('lastupdate', ''),
            })

    return carpark_id, normalized_entries


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def carpark_list(request):
    """
    Proxy HK Transport Dept carpark info with optional search/filter.
    Query params: search, district
    """
    data = _fetch_hk_data(
        HK_API_URL,
        'hk_carpark_info_zh_tw',
        CACHE_TIMEOUT_INFO,
        params={'data': 'info', 'lang': 'zh_TW'},
    )
    if data is None:
        return Response({'message': '無法獲取停車場資料，請稍後再試'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        raw_carparks = data.get('results', [])
    except (AttributeError, KeyError):
        return Response({'message': '資料格式錯誤'}, status=status.HTTP_502_BAD_GATEWAY)

    carparks = [_normalize_carpark_info(carpark) for carpark in raw_carparks]

    search = request.query_params.get('search', '').strip()
    district = request.query_params.get('district', '').strip()

    if search:
        search_lower = search.lower()
        carparks = [
            c for c in carparks
            if search_lower in c.get('name', '').lower()
            or search_lower in c.get('nameEn', '').lower()
            or search_lower in c.get('addressTc', '').lower()
            or search_lower in c.get('addressEn', '').lower()
        ]

    if district:
        carparks = [
            c for c in carparks
            if district.lower() in c.get('districtTc', '').lower()
            or district.lower() in c.get('districtEn', '').lower()
        ]

    # Attach favorite status for the current user
    user_fav_ids = set(
        Favorite.objects.filter(user=request.user).values_list('carpark_id', flat=True)
    )
    for c in carparks:
        c['isFavorite'] = c.get('carparkNo', '') in user_fav_ids

    return Response({'total': len(carparks), 'carparks': carparks})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def carpark_vacancy(request):
    """Real-time vacancy data, optionally filtered by carparkNo list."""
    data = _fetch_hk_data(
        HK_API_URL,
        'hk_carpark_vacancy_zh_tw',
        CACHE_TIMEOUT_VACANCY,
        params={'data': 'vacancy', 'lang': 'zh_TW'},
    )
    if data is None:
        return Response({'message': '無法獲取空位資料，請稍後再試'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    try:
        vacancies = data.get('results', [])
    except (AttributeError, KeyError):
        return Response({'message': '資料格式錯誤'}, status=status.HTTP_502_BAD_GATEWAY)

    carpark_ids = request.query_params.get('ids', '').strip()
    if carpark_ids:
        id_set = set(carpark_ids.split(','))
        vacancies = [v for v in vacancies if v.get('park_Id', '') in id_set]

    # Group vacancies by carparkNo
    vacancy_map = {}
    for v in vacancies:
        pk_no, normalized_entries = _normalize_vacancy_data(v)
        vacancy_map[pk_no] = normalized_entries

    return Response({'vacancies': vacancy_map})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mapbox_token(request):
    """Return Mapbox public token to authenticated users only."""
    token = settings.MAPBOX_TOKEN
    if not token:
        return Response({'message': 'Mapbox token 未配置'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    return Response({'token': token})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorite_list(request):
    favorites = Favorite.objects.filter(user=request.user)
    return Response(FavoriteSerializer(favorites, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def favorite_add(request):
    serializer = FavoriteCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        favorite = serializer.save()
        return Response(FavoriteSerializer(favorite).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def favorite_remove(request, carpark_id):
    deleted, _ = Favorite.objects.filter(user=request.user, carpark_id=carpark_id).delete()
    if deleted:
        return Response({'message': '已取消收藏'})
    return Response({'message': '收藏記錄不存在'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def favorite_check(request, carpark_id):
    exists = Favorite.objects.filter(user=request.user, carpark_id=carpark_id).exists()
    return Response({'isFavorite': exists})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def districts(request):
    """Return list of HK districts from cached carpark data."""
    data = _fetch_hk_data(
        HK_API_URL,
        'hk_carpark_info_zh_tw',
        CACHE_TIMEOUT_INFO,
        params={'data': 'info', 'lang': 'zh_TW'},
    )
    if data is None:
        return Response({'districts': []})
    carparks = data.get('results', [])
    district_set = set()
    for c in carparks:
        d_tc = c.get('district', '').strip()
        if d_tc:
            district_set.add(d_tc)
    return Response({'districts': sorted(district_set)})
