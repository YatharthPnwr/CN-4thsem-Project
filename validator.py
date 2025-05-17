
import re

def validate_ipv4_syntax(ip_string):
    
    reasons = []
    is_valid = True

    
    if not re.fullmatch(r"[0-9\.]+", ip_string):
        reasons.append(f"IP address '{ip_string}' contains invalid characters (only digits and '.' allowed).")
        return False, reasons

    octets = ip_string.split('.')

    if len(octets) != 4:
        reasons.append(f"Number of Octets ({len(octets)}) not equal to 4.")
        is_valid = False
        
        return is_valid, reasons

    for i, octet_str in enumerate(octets):
        octet_num = i + 1
        if not octet_str: 
            reasons.append(f"Octet #{octet_num} is empty.")
            is_valid = False
            continue

        if not octet_str.isdigit():
            reasons.append(f"Octet #{octet_num} ('{octet_str}') is not a number.")
            is_valid = False
            continue

        if len(octet_str) > 1 and octet_str.startswith('0'):
            reasons.append(f"Octet #{octet_num} ('{octet_str}') has a leading zero (e.g., '01' should be '1').")
            is_valid = False
           

        try:
            value = int(octet_str)
            if not (0 <= value <= 255):
                reasons.append(f"Value of Octet #{octet_num} ('{value}') should be between 0 and 255.")
                is_valid = False
        except ValueError:
            
            reasons.append(f"Octet #{octet_num} ('{octet_str}') could not be converted to an integer.")
            is_valid = False

    if not reasons and not is_valid:
        reasons.append("Unknown validation error.")

    return is_valid, reasons

