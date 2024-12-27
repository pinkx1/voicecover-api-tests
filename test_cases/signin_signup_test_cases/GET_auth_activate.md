1. **Successful user activation.**  
   Verify user activation with a valid value for the `activate_code` parameter.  
   The server is expected to return a status code `200` and the response body contains `{“success”: true}`.

2. **Activation with an invalid activation code.**  
   Checking the server response to the use of an invalid value in the `activate_code` parameter.  
   The server is expected to return a status code ``422`` and the response body contains a description of the error in the format:  
   ``json
   {
     { “detail”: [
       {
         { “loc”: [ “query”, “activate_code”,]
         “msg": ‘Invalid activation code’,
         “type": ”value_error”
       }
     ]
   }
3. **Lack of activate_code parameter.**
Checks the server response if the `activate_code` parameter is missing from the request.
The server is expected to return a status code of `422` and the response body contains an error description indicating the absence of the mandatory parameter.
4. **Empty value of activate_code** parameter.
Check the server's response to a request with an empty value for the `activate_code` parameter (e.g., `/auth/activate?activate_code=`).
The server is expected to return a status code `422` and the response body contains a description of the error.
5. **Reactivation Attempt**.
Checks the server's response to reactivate a previously activated code.
It is expected that the server returns status code `400` or `422` and the response body contains an error description.
