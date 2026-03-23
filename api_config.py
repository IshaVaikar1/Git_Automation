API_FLOW_CONFIG = [
    {
        "name": "login",
        "method": "POST",
        "endpoint": "/api/v1/token",
        "body": {
            "userId": "{userId}",
            "password": "{password}",
            # "bankName": "janaatasahakaribank"
        },
        "headers": {"Content-Type": "application/json",
                    # "{headerName}" : "{headerValue}",
                    # "{userAgent}" : "{userAgentValue}"                    
                    }
    },
   

    {
        "name": "usageReport",
        "method": "POST",
        "endpoint": "/api/analysis/usage/report",
        "headers": {
            "Authorization": "Bearer {token}",
            "Content-Type": "application/json",
            # "{headerName}" : "{headerValue}",
            # "{userAgent}" : "{userAgentValue}"  
        },
        "body": {
            "startDate": "{startDate}",
            "endDate": "{endDate}"
        }
    },
]
