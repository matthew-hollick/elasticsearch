# Exporter Authentication

This document explains how to configure authentication for Prometheus exporters used with the SNMP Bridge.

## Overview

The SNMP Bridge supports authentication when connecting to secured Prometheus exporters. This includes:

1. **Basic Authentication** - Username and password
2. **Bearer Token Authentication** - OAuth or similar token-based auth
3. **API Key Authentication** - Custom API key headers
4. **TLS/SSL** - Certificate-based authentication and encryption

## Configuring Exporters to Use Authentication

### SNMP Exporter

The SNMP Exporter supports TLS and basic authentication through a web configuration file. To enable authentication:

1. Create a web configuration file (see example in `examples/snmp_exporter_web_config.yml`)
2. Start the SNMP Exporter with the `--web.config.file` flag:

```bash
./snmp_exporter --web.config.file=snmp_exporter_web_config.yml
```

#### Creating Password Hashes

The web configuration file requires bcrypt-hashed passwords. Generate them using:

```bash
htpasswd -nBC 10 "" | tr -d ':\n'
```

This command will prompt for a password and output the hashed value to use in the configuration file.

## Configuring the SNMP Bridge to Authenticate with Exporters

### Basic Authentication

To configure the SNMP Bridge to use basic authentication when connecting to an exporter:

```json
"exporters": {
  "snmp_exporter": {
    "type": "snmp",
    "url": "https://snmp-exporter.hedgehog.internal:9116",
    "auth": {
      "username": "hedgehog_exporter_user",
      "password": "secure_password_here"
    }
  }
}
```

### Bearer Token Authentication

For exporters that use bearer token authentication:

```json
"exporters": {
  "custom_exporter": {
    "type": "custom",
    "url": "https://custom-exporter.hedgehog.internal:9100",
    "auth": {
      "bearer_token": "your-bearer-token-here"
    }
  }
}
```

### API Key Authentication

For exporters that use API key authentication:

```json
"exporters": {
  "api_exporter": {
    "type": "api",
    "url": "https://api-exporter.hedgehog.internal:9200",
    "auth": {
      "api_key": "your-api-key-here"
    }
  }
}
```

### TLS Configuration

To configure TLS for secure connections:

```json
"exporters": {
  "secure_exporter": {
    "type": "secure",
    "url": "https://secure-exporter.hedgehog.internal:9116",
    "tls": {
      "verify": true,
      "ca_cert": "/etc/ssl/certs/ca-certificates.crt",
      "client_cert": "/etc/ssl/certs/client.crt",
      "client_key": "/etc/ssl/private/client.key"
    }
  }
}
```

Options:
- `verify`: Whether to verify TLS certificates (default: true)
- `ca_cert`: Path to CA certificate file for verifying server certificates
- `client_cert`: Path to client certificate file for client authentication
- `client_key`: Path to client key file for client authentication

## Security Considerations

1. **Use HTTPS**: Always use HTTPS when authentication is enabled to prevent credentials from being transmitted in plaintext.

2. **Least Privilege**: Create dedicated users for the SNMP Bridge with only the permissions needed.

3. **Credential Rotation**: Regularly rotate passwords and tokens.

4. **Secure Storage**: Store the runtime configuration securely, as it contains sensitive credentials.

5. **Audit Logging**: Enable audit logging on exporters to track authentication attempts.

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Verify credentials in the runtime configuration
   - Check that the exporter's web configuration file has the correct user/password

2. **TLS Certificate Issues**:
   - Ensure CA certificates are correctly installed
   - Verify certificate paths in the configuration
   - Check certificate expiration dates

3. **Permission Denied**:
   - Verify that the user has appropriate permissions
   - Check file permissions for certificate and key files
