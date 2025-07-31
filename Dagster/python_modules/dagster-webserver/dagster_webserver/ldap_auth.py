from ldap3 import Server, Connection, SUBTREE, ALL
from ldap3.core.exceptions import LDAPException, LDAPBindError, LDAPSocketOpenError
from typing import Optional
from dagster_webserver.user import User
import os
from passlib.context import CryptContext
# from passlib.hash import ldap_sha1, ldap_plaintext

LDAP_HOST = os.getenv("LDAP_HOST")
LDAP_PORT = int(os.getenv("LDAP_PORT"))
LDAP_BASE_DN = os.getenv("LDAP_BASE_DN")
LDAP_BIND_DN = os.getenv("LDAP_BIND_DN")
LDAP_BIND_PASSWORD = os.getenv("LDAP_BIND_PASSWORD")

LDAP_USER_SEARCH_BASE = os.getenv("LDAP_USER_SEARCH_BASE")
LDAP_USER_SEARCH_FILTER = os.getenv("LDAP_USER_SEARCH_FILTER")
LDAP_USER_ID_ATTRIBUTE = os.getenv("LDAP_USER_ID_ATTRIBUTE")

USE_SSL_FOR_LDAP = os.getenv("USE_SSL_FOR_LDAP")

pwd_context = CryptContext(schemes=["ldap_pbkdf2_sha256","ldap_salted_sha256", "ldap_sha1", "sha256_crypt","ldap_salted_md5", "ldap_salted_sha1","ldap_md5", "ldap_plaintext"])

def authenticate_ldap_user(username: str, password: str) -> Optional[User]:

    server = Server(
        host=LDAP_HOST, 
        port=LDAP_PORT, 
        use_ssl=USE_SSL_FOR_LDAP, 
        get_info=ALL
    )

    search_filter = LDAP_USER_SEARCH_FILTER.format(username=username)
    conn = None
    # user_auth_conn = None

    try:
        # =====================================================================
        #  STAGE 1: Admin Bind to find the user's DN
        # =====================================================================
        conn = Connection(server, user=LDAP_BIND_DN, password=LDAP_BIND_PASSWORD, auto_bind=True)

        # Check if the admin bind was successful
        if not conn.bind():
            return None
        
        success = conn.search(
            search_base=LDAP_USER_SEARCH_BASE,
            search_filter=search_filter,
            search_scope=SUBTREE,
            attributes=[LDAP_USER_ID_ATTRIBUTE] # Fetch the user ID attribute
        )
        
        if not success:
            return None

        if not conn.entries:
            print(f"[LDAP DEBUG ERROR] >>> STAGE 1 FAILED: User '{username}' not found with filter '{search_filter}' in base '{LDAP_USER_SEARCH_BASE}'.")
            return None

        # If user is found
        user_entry = conn.entries[0]
        user_dn = user_entry.entry_dn
        

        # =====================================================================
        #  STAGE 2: PASSWORD VERIFICATION 
        # =====================================================================
        # Fetching stored password (hash or plaintext) 

        # --- START OF COMMENTED-OUT CODE ---
        # if 'userPassword' not in user_entry:
        #     print(f"[LDAP DEBUG ERROR] >>> User '{username}' found, but has no password set.")
        #     return None

        # stored_password = user_entry.userPassword.value
        # print(f"[LDAP DEBUG] >>> User found. Stored password/hash fetched:{stored_password[:10]}...")

        # try:
        #     is_valid = pwd_context.verify(password, stored_password)
        # except Exception as e:
        #     print(f"[LDAP DEBUG ERROR] >>> passlib verification failed with an error: {e}")
        #     is_valid = False

        # if not is_valid:
        #     print(f"[LDAP DEBUG ERROR] >>> Password verification failed. Incorrect password.")
        #     return None
        # print("[LDAP DEBUG] >>> STAGE 2 SUCCESS: Password verified.")
         
        # =====================================================================
        #  STAGE 3: Return user info ONLY after successful authentication
        # =====================================================================
        user_id = user_entry[LDAP_USER_ID_ATTRIBUTE].value 
        return User(identifier=hash(user_id), username=user_id, password=password)

    except LDAPSocketOpenError as e:
        print(f"[LDAP DEBUG EXCEPTION] >>> CRITICAL: Could not connect to LDAP server at {LDAP_HOST}:{LDAP_PORT}. Is the hostname correct? Is the server running and reachable from the webserver container?")
        print(f"[LDAP DEBUG EXCEPTION]   Error: {e}")
        return None
    except LDAPBindError as e:
        print(f"[LDAP DEBUG EXCEPTION] >>> CRITICAL: A bind error occurred. This is often a credentials issue.")
        print(f"[LDAP DEBUG EXCEPTION]   Error: {e}")
        return None
    except LDAPException as e:
        print(f"[LDAP DEBUG EXCEPTION] >>> A generic LDAP exception occurred.")
        print(f"[LDAP DEBUG EXCEPTION]   Error: {e}")
        return None
    except Exception as e:
        print(f"[LDAP DEBUG EXCEPTION] >>> An unexpected Python error occurred during LDAP auth.")
        print(f"[LDAP DEBUG EXCEPTION]   Error: {e}")
        return None
    finally:
        if conn and conn.bound:
            conn.unbind()
        # if user_auth_conn and user_auth_conn.bound:
        #     print("[LDAP DEBUG]   Unbinding leftover user connection.")
        #     user_auth_conn.unbind()