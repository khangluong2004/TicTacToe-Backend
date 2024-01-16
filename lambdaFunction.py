import json

def lambda_handler(event, context):
    # TODO implement
    # Check the authorizer
    
    
    # Test echoing the input
    requestBody = json.loads(event["body"])
    
    return {
        'statusCode': 200,
        'body': json.dumps((requestBody["numX"], requestBody["numO"]))
    }
