#!/usr/bin/env python3
import sys
import ipaddress
import re

def parse_input(input_str):
    """Parse various IP formats and return standard IPv4 address"""
    input_str = input_str.strip()

    # Standard IPv4
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', input_str):
        return input_str

    # 32-bit decimal
    if input_str.isdigit():
        ip_int = int(input_str)
        return str(ipaddress.IPv4Address(ip_int))

    # 32-bit hex (0x prefix)
    if input_str.startswith('0x'):
        ip_int = int(input_str, 16)
        return str(ipaddress.IPv4Address(ip_int))

    # IPv6 mapped (::ffff:x.x.x.x)
    if input_str.startswith('::ffff:'):
        return input_str[7:]

    # Integer overflow format (a.b.xyz where xyz > 255)
    if re.match(r'^\d+\.\d+\.\d+$', input_str):
        parts = input_str.split('.')
        if len(parts) == 3 and int(parts[2]) > 255:
            a, b, combined = int(parts[0]), int(parts[1]), int(parts[2])
            c, d = divmod(combined, 256)
            return f"{a}.{b}.{c}.{d}"

    # Truncated format (missing octets filled with zeros, last part goes to end)
    if re.match(r'^\d+(\.\d+){1,2}$', input_str):
        parts = input_str.split('.')
        if len(parts) == 2:
            a, combined = int(parts[0]), int(parts[1])
            if combined <= 255:
                return f"{a}.0.0.{combined}"
            else:
                # Handle cases like 1.300 -> 1.0.1.44
                b, remainder = divmod(combined, 256)
                c, d = divmod(remainder, 1) if remainder < 256 else divmod(remainder, 256)
                return f"{a}.0.{int(combined // 256)}.{combined % 256}"
        elif len(parts) == 3 and all(int(p) <= 255 for p in parts):
            return f"{parts[0]}.{parts[1]}.0.{parts[2]}"

    # Octal format
    if re.match(r'^0\d+(\.\d+){3}$', input_str) or all(c.isdigit() or c == '.' for c in input_str):
        try:
            parts = input_str.split('.')
            decimal_parts = []
            for part in parts:
                if part.startswith('0') and len(part) > 1:
                    decimal_parts.append(str(int(part, 8)))
                else:
                    decimal_parts.append(part)
            return '.'.join(decimal_parts)
        except ValueError:
            pass

    return None

def convert_ipv4(ip_str):
    """Convert IPv4 address to various formats"""
    try:
        ip = ipaddress.IPv4Address(ip_str)
        ip_int = int(ip)
        octets = [int(x) for x in ip_str.split('.')]

        print(f"{'Standard IPv4:':18} {ip_str}")
        print(f"{'32-bit decimal:':18} {ip_int}")
        print(f"{'32-bit hex:':18} 0x{ip_int:08x}")
        print(f"{'IPv6 mapped:':18} ::ffff:{ip}")

        # Truncated format
        truncated_parts = []
        for i, octet in enumerate(octets):
            truncated_parts.append(str(octet))
            if all(x == 0 for x in octets[i+1:]):
                break
        truncated = '.'.join(truncated_parts)
        if truncated != ip_str:
            print(f"{'Truncated:':18} {truncated}")

        # Integer overflow format
        if octets[2] >= 1 or octets[3] >= 1:
            combined = octets[2] * 256 + octets[3]
            if octets[1] == 0:
                overflow = f"{octets[0]}.{combined}"
            else:
                overflow = f"{octets[0]}.{octets[1]}.{combined}"
            print(f"{'Overflow/truncate:':18} {overflow}")

        # Octal format
        octal = '.'.join(f"0{x:o}" if x >= 8 else f"{x:o}" for x in octets)
        print(f"{'Octal:':18} {octal}")

    except ipaddress.AddressValueError:
        print(f"Error: Invalid IPv4 address '{ip_str}'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ipfoo.py <IP_address_or_format>")
        sys.exit(1)

    input_value = sys.argv[1]

    # Try to parse the input as various formats
    parsed_ip = parse_input(input_value)

    if parsed_ip:
        convert_ipv4(parsed_ip)
    else:
        print(f"Error: Could not parse '{input_value}' as any known IP format")
