import json
from botLogic import minimax, unmaskBoard

cache = {}

def lambda_handler(event, context):
    # TODO implement
    # Check the authorizer
    
    
    # Test echoing the input
    requestBody = json.loads(event["body"])
    numX = requestBody["numX"]
    numO = requestBody["numO"]
    isX = requestBody["isX"]
    
    receivedBoard = unmaskBoard(numX, numO)
    
    nextMove = (0, 0)
    if ((numX, numO, isX) in cache):
        nextMove = cache[(numX, numO, isX)]
    else:
        nextMove = minimax(receivedBoard, isX)
        cache[(numX, numO, isX)] = nextMove
    
    return {
        'statusCode': 200,
        'body': json.dumps(nextMove),
        'headers': {
            "Access-Control-Allow-Origin": "*"
        }
    }
