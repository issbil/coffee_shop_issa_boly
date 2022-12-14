import json
from flask import request, _request_ctx_stack, abort, jsonify
from functools import wraps
from jose import jwt
from urllib.request import urlopen


# AUTH0_DOMAIN = 'udacity-fsnd.auth0.com'
# ALGORITHMS = ['RS256']
# API_AUDIENCE = 'dev'
AUTH0_DOMAIN = 'issbil.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'test-api'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get('Authorization', None)
    if not auth:
        authorization_header_missing()

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        header_not_start_with_bearer()

    elif len(parts) == 1:
        return token_not_found()

    elif len(parts) > 2:
        not_bearer_token()

    token = parts[1]
    return token

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        authorization_maform()

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            return token_expired()

        except jwt.JWTClaimsError:
            invalid_claims()
        except Exception:
            unable_to_parse_token()
            
    key_not_found()

'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator


 
'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

#authorization header missing
def authorization_header_missing():
    raise AuthError({
        'code': 'authorization_header_missing',
        'description': 'Authorization header is expected.'
    }, 401)


#Invalid header 
def header_not_start_with_bearer():
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Authorization header must start with "Bearer".'
    }, 401)


#Token not found
def token_not_found():
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Token not found.'
    }, 401)

 
#Expected Bearer token
def not_bearer_token():
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Authorization header must be bearer token.'
    }, 401)


#Authorization malform
def authorization_maform():
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Authorization malformed.'
    }, 401)


#Token expired
def token_expired():
    raise AuthError({
        'code': 'token_expired',
        'description': 'Token expired.'
    }, 401)


#Incorrect claims
def invalid_claims():
    raise AuthError({
        'code': 'invalid_claims',
        'description': 'Incorrect claims. Please, check the audience and issuer.'
    }, 401)


#Unable to parse token
def unable_to_parse_token():
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to parse authentication token.'
    }, 400)


#Key not found
def key_not_found():
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)

 
#Permissions not include in JWT
def permissions_not_in_jwt():
    raise AuthError({
        'code': 'invalid_claims',
        'description': 'Permissions not included in JWT.'
    }, 400)


#Permission not found
def permission_not_found():
    raise AuthError({
        'code': 'unauthorized',
        'description': 'Permission not found.'
    }, 403)
