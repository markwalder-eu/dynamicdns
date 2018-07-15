

def script(event, context):
    file = open("dynamicdns/scripts/dynamic-dns-client", "r") 
    content = file.read()
    file.close()

    headers = {
        "Content-Type": "text/plain"
    }
    body = content
    response = {
        "statusCode": 200,
        "headers": headers,
        "body": body
    }
    return response
 