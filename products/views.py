from django.shortcuts import render
from . serialiser import ModelSerialiser
from . models import Product
from rest_framework import generics
from django.core.cache import cache
from rest_framework.response import Response

CACHE_TTL = 60 * 5

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ModelSerialiser

    def list(self,request,*args,**kwargs):
        name = request.query_params.get("name","").strip().lower()
        version = cache.get("products_version",1)
        key = f"products:v{version}:{name}"

        data = cache.get(key)
        if data is None:
            qs =   self.get_queryset()
            if name:
                qs = qs.filter(name__icontains=name)
            data = ModelSerialiser(qs,many=True).data
            cache.set(key,list(data),CACHE_TTL)
        return Response(data)

    def perform_create(self, serializer):
        serializer.save()
        cache.set("products_version",cache.get("products_version",1)+1,None)