#!/usr/bin/env python3

import argparse
import json
import random
import time
import uuid
import hashlib
import requests
from datetime import datetime, timezone
from jinja2 import Template

# Elasticsearch connection details
ES_HOST = "https://localhost:9200"
ES_USER = "elastic"
ES_PASS = "changeme"
INDEX = "metrics-test"

# Host configuration
KAFKA_HOSTS = ["kafka-broker-1", "kafka-broker-2", "kafka-broker-3"]
MYSQL_HOST = "mysql-server-1"
ALL_HOSTS = KAFKA_HOSTS + [MYSQL_HOST]

# Service configuration
KAFKA_VERSION = "3.4.0"
MYSQL_VERSION = "8.0.32"

# Disable certificate verification for self-signed certs
VERIFY_SSL = False


def random_float(min_val, max_val, precision=2):
    """Generate a random float between min_val and max_val with specified precision."""
    return round(random.uniform(min_val, max_val), precision)


def random_int(min_val, max_val):
    """Generate a random integer between min_val and max_val."""
    return random.randint(min_val, max_val)


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4()).upper()


def generate_md5(text):
    """Generate an MD5 hash of the input text."""
    return hashlib.md5(text.encode()).hexdigest()


def get_timestamp():
    """Get current timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def generate_metrics(host, service_type):
    """Generate metrics for a given host and service type."""
    timestamp = get_timestamp()

    # Common metrics
    cpu_user = random_float(5, 80)
    cpu_system = random_float(2, 30)
    cpu_idle = random_float(5, 90)
    cpu_iowait = random_float(0, 15)
    mem_used_pct = random_float(40, 90)

    # Service-specific metrics
    if service_type == "kafka":
        # Kafka metrics
        request_total = random_int(1000, 10000)
        request_failed = random_int(0, 100)
        request_time_avg = random_float(1, 50)
        request_time_max = request_time_avg + random_float(10, 100)
        network_io_rate = random_float(1, 100)
        messages_in_rate = random_float(100, 1000)
        bytes_in_rate = random_float(10000, 100000)
        bytes_out_rate = random_float(10000, 100000)
        bytes_rejected_rate = random_float(0, 10)
        replication_leader_count = random_int(1, 10)

        service_version = KAFKA_VERSION
        ip_suffix = 100 + KAFKA_HOSTS.index(host)
        metric_category = "messaging"
        event_module = "kafka"
        event_dataset = "kafka.request"
        metricset_name = "request"

    elif service_type == "mysql":
        # MySQL metrics
        threads_connected = random_int(5, 100)
        threads_running = random_int(1, 20)
        threads_created = random_int(100, 1000)
        threads_cached = random_int(0, 50)
        connections_max = random_int(150, 200)
        connections_total = random_int(1000, 10000)
        aborted_clients = random_int(0, 50)
        aborted_connects = random_int(0, 20)
        queries = random_int(10000, 100000)
        slow_queries = random_int(0, 100)
        innodb_buffer_pool_pages_total = random_int(8000, 10000)
        innodb_buffer_pool_pages_free = random_int(1000, 3000)
        innodb_buffer_pool_pages_dirty = random_int(0, 1000)
        innodb_buffer_pool_read_requests = random_int(10000, 100000)
        innodb_buffer_pool_reads = random_int(0, 1000)

        # Memory metrics
        mem_total = random_int(8000000000, 16000000000)
        mem_used = int(mem_total * (mem_used_pct / 100))
        mem_free = mem_total - mem_used
        mem_cached = random_int(1000000000, 2000000000)
        mem_buffers = random_int(500000000, 1000000000)

        # Swap metrics
        swap_total = random_int(4000000000, 8000000000)
        swap_used = random_int(0, 1000000000)
        swap_free = swap_total - swap_used

        service_version = MYSQL_VERSION
        ip_suffix = 150
        metric_category = "database"
        event_module = "mysql"
        event_dataset = "mysql.status"
        metricset_name = "status"

    # Render template
    template_str = """
    {
      "@timestamp": "{{ timestamp }}",
      "agent": {
        "type": "metricbeat",
        "version": "8.8.0",
        "hostname": "{{ host }}",
        "ephemeral_id": "{{ uuid }}",
        "id": "{{ md5 }}"
      },
      "service": {
        "type": "{{ service_type }}",
        "name": "{{ service_type }}",
        "version": "{{ service_version }}",
        "environment": "production"
      },
      "host": {
        "name": "{{ host }}",
        "hostname": "{{ host }}",
        "architecture": "x86_64",
        "os": {
          "platform": "linux",
          "name": "Ubuntu",
          "family": "debian",
          "version": "22.04.2 LTS",
          "kernel": "5.15.0-76-generic"
        },
        "ip": "10.10.10.{{ ip_suffix }}"
      },
      "event": {
        "module": "{{ event_module }}",
        "dataset": "{{ event_dataset }}",
        "duration": 4572385
      },
      "metricset": {
        "name": "{{ metricset_name }}",
        "period": 60000
      },
      {% if service_type == "kafka" %}
      "kafka": {
        "request": {
          "total": {{ request_total }},
          "failed": {{ request_failed }},
          "time": {
            "avg": {
              "ms": {{ request_time_avg }}
            },
            "max": {
              "ms": {{ request_time_max }}
            }
          }
        },
        "network": {
          "io": {
            "rate": {{ network_io_rate }}
          }
        },
        "messages": {
          "in": {
            "rate": {{ messages_in_rate }}
          }
        },
        "bytes": {
          "in": {
            "rate": {{ bytes_in_rate }}
          },
          "out": {
            "rate": {{ bytes_out_rate }}
          },
          "rejected": {
            "rate": {{ bytes_rejected_rate }}
          }
        },
        "replication": {
          "leader": {
            "count": {{ replication_leader_count }}
          }
        }
      },
      {% elif service_type == "mysql" %}
      "mysql": {
        "status": {
          "threads": {
            "connected": {{ threads_connected }},
            "running": {{ threads_running }},
            "created": {{ threads_created }},
            "cached": {{ threads_cached }}
          },
          "connections": {{ connections_total }},
          "aborted": {
            "clients": {{ aborted_clients }},
            "connects": {{ aborted_connects }}
          },
          "queries": {{ queries }},
          "slow_queries": {{ slow_queries }},
          "innodb": {
            "buffer_pool": {
              "pages": {
                "total": {{ innodb_buffer_pool_pages_total }},
                "free": {{ innodb_buffer_pool_pages_free }},
                "dirty": {{ innodb_buffer_pool_pages_dirty }}
              },
              "read": {
                "requests": {{ innodb_buffer_pool_read_requests }}
              },
              "reads": {{ innodb_buffer_pool_reads }}
            }
          }
        }
      },
      {% endif %}
      "system": {
        "cpu": {
          "user": {
            "pct": {{ cpu_user / 100 }}
          },
          "system": {
            "pct": {{ cpu_system / 100 }}
          },
          "idle": {
            "pct": {{ cpu_idle / 100 }}
          },
          "iowait": {
            "pct": {{ cpu_iowait / 100 }}
          },
          "total": {
            "pct": {{ (100 - cpu_idle) / 100 }}
          }
        },
        "memory": {
          {% if service_type == "mysql" %}
          "total": {{ mem_total }},
          "used": {
            "bytes": {{ mem_used }},
            "pct": {{ mem_used / mem_total }}
          },
          "free": {{ mem_free }},
          "actual": {
            "free": {{ mem_free + mem_cached + mem_buffers }},
            "used": {
              "bytes": {{ mem_used - mem_cached - mem_buffers }},
              "pct": {{ (mem_used - mem_cached - mem_buffers) / mem_total }}
            }
          },
          "swap": {
            "total": {{ swap_total }},
            "free": {{ swap_free }},
            "used": {
              "bytes": {{ swap_used }},
              "pct": {{ swap_used / swap_total }}
            }
          }
          {% else %}
          "used": {
            "pct": {{ mem_used_pct / 100 }}
          }
          {% endif %}
        }
      },
      "metadata": {
        "slo_relevant": true,
        "metric_category": "{{ metric_category }}"
      }
    }
    """

    template = Template(template_str)

    # Build context dictionary with all variables
    context = {
        "timestamp": timestamp,
        "host": host,
        "uuid": generate_uuid(),
        "md5": generate_md5(host),
        "service_type": service_type,
        "service_version": service_version,
        "ip_suffix": ip_suffix,
        "event_module": event_module,
        "event_dataset": event_dataset,
        "metricset_name": metricset_name,
        "metric_category": metric_category,
        "cpu_user": cpu_user,
        "cpu_system": cpu_system,
        "cpu_idle": cpu_idle,
        "cpu_iowait": cpu_iowait,
        "mem_used_pct": mem_used_pct,
    }

    # Add service-specific context variables
    if service_type == "kafka":
        context.update(
            {
                "request_total": request_total,
                "request_failed": request_failed,
                "request_time_avg": request_time_avg,
                "request_time_max": request_time_max,
                "network_io_rate": network_io_rate,
                "messages_in_rate": messages_in_rate,
                "bytes_in_rate": bytes_in_rate,
                "bytes_out_rate": bytes_out_rate,
                "bytes_rejected_rate": bytes_rejected_rate,
                "replication_leader_count": replication_leader_count,
            }
        )
    elif service_type == "mysql":
        context.update(
            {
                "threads_connected": threads_connected,
                "threads_running": threads_running,
                "threads_created": threads_created,
                "threads_cached": threads_cached,
                "connections_max": connections_max,
                "connections_total": connections_total,
                "aborted_clients": aborted_clients,
                "aborted_connects": aborted_connects,
                "queries": queries,
                "slow_queries": slow_queries,
                "innodb_buffer_pool_pages_total": innodb_buffer_pool_pages_total,
                "innodb_buffer_pool_pages_free": innodb_buffer_pool_pages_free,
                "innodb_buffer_pool_pages_dirty": innodb_buffer_pool_pages_dirty,
                "innodb_buffer_pool_read_requests": innodb_buffer_pool_read_requests,
                "innodb_buffer_pool_reads": innodb_buffer_pool_reads,
                "mem_total": mem_total,
                "mem_used": mem_used,
                "mem_free": mem_free,
                "mem_cached": mem_cached,
                "mem_buffers": mem_buffers,
                "swap_total": swap_total,
                "swap_used": swap_used,
                "swap_free": swap_free,
            }
        )

    rendered = template.render(**context)

    return json.dumps(json.loads(rendered))


def send_to_elasticsearch(data, host_type):
    """Send metrics to Elasticsearch."""
    url = f"{ES_HOST}/{INDEX}/_doc"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(
            url, data=data, headers=headers, auth=(ES_USER, ES_PASS), verify=VERIFY_SSL
        )

        if response.status_code >= 200 and response.status_code < 300:
            print(f"Successfully sent {host_type} metrics to Elasticsearch")
        else:
            print(
                f"Failed to send {host_type} metrics to Elasticsearch: {response.text}"
            )

    except Exception as e:
        print(f"Error sending {host_type} metrics to Elasticsearch: {str(e)}")


def main():
    """Main function to generate and send metrics."""
    parser = argparse.ArgumentParser(
        description="Generate and send metrics to Elasticsearch"
    )
    parser.add_argument(
        "--no-send",
        action="store_true",
        help="Generate metrics but don't send to Elasticsearch",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Interval between metric generations in seconds",
    )
    args = parser.parse_args()

    try:
        while True:
            for host in KAFKA_HOSTS:
                print(f"Generating Kafka metrics for {host}...")
                data = generate_metrics(host, "kafka")

                if args.no_send:
                    print(data)
                else:
                    send_to_elasticsearch(data, f"Kafka ({host})")

            print(f"Generating MySQL metrics for {MYSQL_HOST}...")
            data = generate_metrics(MYSQL_HOST, "mysql")

            if args.no_send:
                print(data)
            else:
                send_to_elasticsearch(data, f"MySQL ({MYSQL_HOST})")

            if args.interval > 0:
                print(f"Waiting {args.interval} seconds before next generation...")
                time.sleep(args.interval)
            else:
                break

    except KeyboardInterrupt:
        print("Generator stopped by user")


if __name__ == "__main__":
    main()
