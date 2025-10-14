def extract_credentials(conn_info:str)->(str, str, str):
    """
    Extract credentials based on conn_info
    """
    auth = None
    base_url = None
    user = None
    password = None

    if '@' in conn_info:
        auth, base_url = conn_info.split("@")
    else:
        return conn_info


    if auth and ':' in auth:
        user, password = auth.split(":")
    if not auth:
        raise ValueError(f"Video Connection format must be [USER:PASSWORD]@[IP:PORT]")

    return base_url, user, password
