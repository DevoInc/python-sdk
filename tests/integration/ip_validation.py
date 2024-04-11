import re


def is_valid_ip(ip_str):
    # Regular expression pattern to match IPv4 address
    ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"

    # Regular expression pattern to match IPv6 address
    ipv6_pattern = r"^(([0-9a-fA-F]{1,4}):){7}([0-9a-fA-F]{1,4})$"

    # Check if the string matches either IPv4 or IPv6 pattern
    if re.match(ipv4_pattern, ip_str):
        return True
    elif re.match(ipv6_pattern, ip_str):
        return True
    else:
        return False


if __name__ == "__main__":
    print("Trying to run module ip_validation.py directly...")
