# SNMP MIB Coverage Analyzer

This tool queries an SNMP endpoint for all OIDs and cross-references them with your MIB files to identify OIDs with and without MIB coverage.

## Features

- Queries an SNMP agent to retrieve all available OIDs
- Parses MIB files to extract OID definitions
- Matches retrieved OIDs against MIB definitions
- Generates a report showing:
  - Which MIBs contain references to each OID
  - OIDs that don't have any MIB coverage
- Multiple output formats (text, JSON, CSV)

## Requirements

- Python 3.6+
- PySNMP
- PySMI
- Net-SNMP tools (for `snmptranslate`)

## Installation

1. Install required Python packages:

```bash
pip install pysnmp pysmi
```

2. Install Net-SNMP tools:

```bash
# On Debian/Ubuntu
sudo apt-get install snmp snmp-mibs-downloader

# On CentOS/RHEL
sudo yum install net-snmp net-snmp-utils

# On macOS
brew install net-snmp
```

## Usage

```bash
python snmp-mib-analyzer.py --host <hostname/IP> [OPTIONS]
```

### Options

- `--host`: SNMP agent hostname or IP (required)
- `--port`: SNMP agent port (default: 161)
- `--community`: SNMP community string (default: public)
- `--mib-dir`: Directory containing MIB files
- `--format`: Output format (text, json, or csv) (default: text)
- `--output`: Output file (default: stdout)

### Example

```bash
# Basic usage
python snmp-mib-analyzer.py --host 192.168.1.100

# Specify MIB directory and output file
python snmp-mib-analyzer.py --host 192.168.1.100 --mib-dir /path/to/mibs --output report.txt

# Generate JSON output
python snmp-mib-analyzer.py --host 192.168.1.100 --format json --output report.json
```

## MIB File Structure

Place your MIB files in a directory and specify it with the `--mib-dir` option. The tool will search for all MIB files in that directory.

## Output Example

### Text Output

```
================================================================================
SNMP MIB Coverage Analysis Report
================================================================================
SNMP Agent: 192.168.1.100:161
Total OIDs retrieved: 425
OIDs with MIB coverage: 378
OIDs without MIB coverage: 47
================================================================================

OIDs with MIB coverage:
--------------------------------------------------------------------------------
OID: 1.3.6.1.2.1.1.1.0
Value: Hardware: x86_64
Name: sysDescr
MIBs: SNMPv2-MIB, RFC1213-MIB
----------------------------------------
...

OIDs without MIB coverage:
--------------------------------------------------------------------------------
OID: 1.3.6.1.4.1.2021.10.1.5.2
Value: 1.51
----------------------------------------
...
```

### JSON Output

JSON output includes detailed information about each OID, including which MIBs it belongs to and its textual name.

### CSV Output

CSV output can be imported into spreadsheet software for further analysis.

## Troubleshooting

### MIB Parsing Errors

If you encounter errors parsing MIB files, check that:
- MIB files are in the correct format
- All dependent MIB files are available in the specified directory
- The user running the script has read permissions for the MIB files

### SNMP Connection Issues

If you have trouble connecting to the SNMP agent:
- Verify the hostname/IP and port are correct
- Check that the community string is correct
- Ensure there are no firewalls blocking the connection
- Verify the SNMP agent is running and properly configured

## License

This tool is provided under the MIT License.