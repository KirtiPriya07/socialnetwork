from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class SocialNetworkPaginationClass(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size =100
    message = ''
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def get_paginated_response(self, data):
        limit = self.request.query_params.get('page_size', 10)
 
        if self.page.paginator.count == 0:
            return Response({
                'status': True,
                "status_code":200,
                "message":"Data not found",
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )
        else:
            return Response({
                'status': True,
                "status_code":200,
                "message":self.message,
                "error":"",
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'count': self.page.paginator.count,
                'page_size':int(limit),
                "data":data}
            )