1. **Authorization with correct credentials.**  
   Verify successful login with correct email and password. The server is expected to return a status code `200` and the response body contains `access_token`, `refresh_token` and user data.

2. **Attempting to log in to an unauthorized account.**  
   Checking the server's response to an attempt to authorize a user with an unconfirmed email. It is expected that the server returns a status code `403` and the response body contains a message about the need to confirm the account.

3. **Authorization with unregistered email.**  
   Checking the server's response to an attempt to log in with an email that is not in the system. The server is expected to return the status code `401` and the response body contains an error message.

4. **Authorization with invalid password.**
   Checks the server response to a login attempt with a valid email but an invalid password. The server is expected to return a status code of `401` and the response body contains an error message.

5. **Authorization with empty email field.**  
   Checking the server's response to the absence of a value in the `email` field. The server is expected to return status code `422` and the response body contains a validation error message.

6. **Authorization with an empty password field.**  
   Checking the server's response to the absence of a value in the `password` field. The server is expected to return a status code `422` and the response body contains a validation error message.

7. **Authorization with an empty request body** 
   Checking the server response for the absence of all parameters in the request body. The server is expected to return status code `422` and the response body contains a validation error message.

8. **Authorization with an additional parameter in the body of the request.**  
   Verify successful authorization if a non-existent parameter (e.g., `extra_param`) is present in the request body. The server is expected to ignore this parameter, return a status code `200`, and the response body contains `access_token`, `refresh_token` and user data.
