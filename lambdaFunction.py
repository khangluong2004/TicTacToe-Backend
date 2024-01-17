import json
from botLogic import minimax, unmaskBoard

def lambda_handler(event, context):
    # TODO implement
    # Check the authorizer
    
    
    # Test echoing the input
    requestBody = json.loads(event["body"])

    # Find the next optimal choice
    receivedBoard = unmaskBoard(requestBody["numX"], requestBody["numO"])
    nextMove = minimax(receivedBoard, requestBody["isX"])
    
    return {
        'statusCode': 200,
        'body': json.dumps(nextMove),
        'headers': {
            "Access-Control-Allow-Origin": "*"
        }
    }
