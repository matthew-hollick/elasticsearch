# Create the metrics-test index
resource "elasticstack_elasticsearch_index" "metrics_test" {
  name = "metrics-test"

  number_of_shards   = 3
  number_of_replicas = 1
  refresh_interval   = "5s"

  mappings = jsonencode({
    "properties" : {
      "@timestamp" : {
        "type" : "date"
      },
      "agent" : {
        "properties" : {
          "type" : {
            "type" : "keyword"
          },
          "version" : {
            "type" : "keyword"
          },
          "hostname" : {
            "type" : "keyword"
          },
          "ephemeral_id" : {
            "type" : "keyword"
          },
          "id" : {
            "type" : "keyword"
          }
        }
      },
      "service" : {
        "properties" : {
          "type" : {
            "type" : "keyword"
          },
          "name" : {
            "type" : "keyword"
          },
          "environment" : {
            "type" : "keyword"
          }
        }
      },
      "host" : {
        "properties" : {
          "name" : {
            "type" : "keyword"
          },
          "hostname" : {
            "type" : "keyword"
          },
          "architecture" : {
            "type" : "keyword"
          },
          "os" : {
            "properties" : {
              "platform" : {
                "type" : "keyword"
              },
              "name" : {
                "type" : "keyword"
              },
              "version" : {
                "type" : "keyword"
              }
            }
          }
        }
      },
      "metadata" : {
        "properties" : {
          "slo_relevant" : {
            "type" : "boolean"
          },
          "metric_category" : {
            "type" : "keyword"
          }
        }
      },
      "kafka" : {
        "properties" : {
          "broker" : {
            "properties" : {
              "address" : {
                "type" : "keyword"
              },
              "id" : {
                "type" : "long"
              },
              "request" : {
                "properties" : {
                  "queue" : {
                    "type" : "long"
                  },
                  "time" : {
                    "properties" : {
                      "avg" : {
                        "properties" : {
                          "ms" : {
                            "type" : "float"
                          }
                        }
                      }
                    }
                  }
                }
              },
              "network" : {
                "properties" : {
                  "io" : {
                    "properties" : {
                      "rate" : {
                        "type" : "float"
                      }
                    }
                  }
                }
              },
              "messages" : {
                "properties" : {
                  "in" : {
                    "properties" : {
                      "rate" : {
                        "type" : "float"
                      }
                    }
                  }
                }
              },
              "offline_partition" : {
                "properties" : {
                  "count" : {
                    "type" : "long"
                  }
                }
              },
              "under_replicated_partition" : {
                "properties" : {
                  "count" : {
                    "type" : "long"
                  }
                }
              }
            }
          }
        }
      },
      "mysql" : {
        "properties" : {
          "status" : {
            "properties" : {
              "threads" : {
                "properties" : {
                  "connected" : {
                    "type" : "long"
                  },
                  "running" : {
                    "type" : "long"
                  }
                }
              },
              "queries" : {
                "type" : "long"
              },
              "slow_queries" : {
                "type" : "long"
              },
              "aborted" : {
                "properties" : {
                  "clients" : {
                    "type" : "long"
                  },
                  "connects" : {
                    "type" : "long"
                  }
                }
              }
            }
          }
        }
      },
      "system" : {
        "properties" : {
          "cpu" : {
            "properties" : {
              "user" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              },
              "system" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              },
              "idle" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              },
              "iowait" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              },
              "total" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              }
            }
          },
          "load" : {
            "properties" : {
              "1" : {
                "type" : "float"
              },
              "5" : {
                "type" : "float"
              },
              "15" : {
                "type" : "float"
              }
            }
          },
          "memory" : {
            "properties" : {
              "total" : {
                "type" : "long"
              },
              "used" : {
                "properties" : {
                  "bytes" : {
                    "type" : "long"
                  },
                  "pct" : {
                    "type" : "float"
                  }
                }
              },
              "free" : {
                "type" : "long"
              },
              "swap" : {
                "properties" : {
                  "total" : {
                    "type" : "long"
                  },
                  "used" : {
                    "properties" : {
                      "bytes" : {
                        "type" : "long"
                      },
                      "pct" : {
                        "type" : "float"
                      }
                    }
                  }
                }
              }
            }
          },
          "network" : {
            "properties" : {
              "in" : {
                "properties" : {
                  "bytes" : {
                    "type" : "long"
                  },
                  "packets" : {
                    "type" : "long"
                  }
                }
              },
              "out" : {
                "properties" : {
                  "bytes" : {
                    "type" : "long"
                  },
                  "packets" : {
                    "type" : "long"
                  }
                }
              }
            }
          }
        }
      }
    }
  })
}

# Create the service_thresholds index
resource "elasticstack_elasticsearch_index" "service_thresholds" {
  name = "service_thresholds"

  number_of_shards   = 1
  number_of_replicas = 1
  refresh_interval   = "10s"

  mappings = jsonencode({
    "properties" : {
      "_enrich_key" : {
        "type" : "keyword"
      },
      "service" : {
        "properties" : {
          "type" : {
            "type" : "keyword"
          },
          "name" : {
            "type" : "keyword"
          },
          "environment" : {
            "type" : "keyword"
          }
        }
      },
      "thresholds" : {
        "type" : "object",
        "enabled" : true,
        "properties" : {
          "kafka" : {
            "properties" : {
              "broker" : {
                "properties" : {
                  "request" : {
                    "properties" : {
                      "queue" : {
                        "properties" : {
                          "warning" : {
                            "type" : "long"
                          },
                          "critical" : {
                            "type" : "long"
                          }
                        }
                      },
                      "time" : {
                        "properties" : {
                          "avg" : {
                            "properties" : {
                              "ms" : {
                                "properties" : {
                                  "warning" : {
                                    "type" : "long"
                                  },
                                  "critical" : {
                                    "type" : "long"
                                  }
                                }
                              }
                            }
                          }
                        }
                      }
                    }
                  },
                  "network" : {
                    "properties" : {
                      "io" : {
                        "properties" : {
                          "rate" : {
                            "properties" : {
                              "warning" : {
                                "type" : "long"
                              },
                              "critical" : {
                                "type" : "long"
                              }
                            }
                          }
                        }
                      }
                    }
                  },
                  "messages" : {
                    "properties" : {
                      "in" : {
                        "properties" : {
                          "rate" : {
                            "properties" : {
                              "warning" : {
                                "type" : "long"
                              },
                              "critical" : {
                                "type" : "long"
                              }
                            }
                          }
                        }
                      }
                    }
                  },
                  "offline_partition" : {
                    "properties" : {
                      "count" : {
                        "properties" : {
                          "warning" : {
                            "type" : "long"
                          },
                          "critical" : {
                            "type" : "long"
                          }
                        }
                      }
                    }
                  },
                  "under_replicated_partition" : {
                    "properties" : {
                      "count" : {
                        "properties" : {
                          "warning" : {
                            "type" : "long"
                          },
                          "critical" : {
                            "type" : "long"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "mysql" : {
            "properties" : {
              "status" : {
                "properties" : {
                  "threads" : {
                    "properties" : {
                      "connected" : {
                        "properties" : {
                          "warning" : {
                            "type" : "long"
                          },
                          "critical" : {
                            "type" : "long"
                          }
                        }
                      },
                      "running" : {
                        "properties" : {
                          "warning" : {
                            "type" : "long"
                          },
                          "critical" : {
                            "type" : "long"
                          }
                        }
                      }
                    }
                  },
                  "slow_queries" : {
                    "properties" : {
                      "warning" : {
                        "type" : "long"
                      },
                      "critical" : {
                        "type" : "long"
                      }
                    }
                  },
                  "aborted" : {
                    "properties" : {
                      "clients" : {
                        "properties" : {
                          "warning" : {
                            "type" : "long"
                          },
                          "critical" : {
                            "type" : "long"
                          }
                        }
                      },
                      "connects" : {
                        "properties" : {
                          "warning" : {
                            "type" : "long"
                          },
                          "critical" : {
                            "type" : "long"
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          },
          "system" : {
            "properties" : {
              "cpu" : {
                "properties" : {
                  "total" : {
                    "properties" : {
                      "pct" : {
                        "properties" : {
                          "warning" : {
                            "type" : "float"
                          },
                          "critical" : {
                            "type" : "float"
                          }
                        }
                      }
                    }
                  },
                  "iowait" : {
                    "properties" : {
                      "pct" : {
                        "properties" : {
                          "warning" : {
                            "type" : "float"
                          },
                          "critical" : {
                            "type" : "float"
                          }
                        }
                      }
                    }
                  }
                }
              },
              "load" : {
                "properties" : {
                  "1" : {
                    "properties" : {
                      "warning" : {
                        "type" : "float"
                      },
                      "critical" : {
                        "type" : "float"
                      }
                    }
                  },
                  "5" : {
                    "properties" : {
                      "warning" : {
                        "type" : "float"
                      },
                      "critical" : {
                        "type" : "float"
                      }
                    }
                  },
                  "15" : {
                    "properties" : {
                      "warning" : {
                        "type" : "float"
                      },
                      "critical" : {
                        "type" : "float"
                      }
                    }
                  }
                }
              },
              "memory" : {
                "properties" : {
                  "used" : {
                    "properties" : {
                      "pct" : {
                        "properties" : {
                          "warning" : {
                            "type" : "float"
                          },
                          "critical" : {
                            "type" : "float"
                          }
                        }
                      }
                    }
                  },
                  "swap" : {
                    "properties" : {
                      "used" : {
                        "properties" : {
                          "pct" : {
                            "properties" : {
                              "warning" : {
                                "type" : "float"
                              },
                              "critical" : {
                                "type" : "float"
                              }
                            }
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  })
}

# Create the service-health index
resource "elasticstack_elasticsearch_index" "service_health" {
  name = "service-health"

  number_of_shards   = 3
  number_of_replicas = 1
  refresh_interval   = "5s"
  codec              = "best_compression"

  mappings = jsonencode({
    "properties" : {
      "service" : {
        "properties" : {
          "type" : {
            "type" : "keyword"
          },
          "name" : {
            "type" : "keyword"
          },
          "environment" : {
            "type" : "keyword"
          }
        }
      },
      "host" : {
        "properties" : {
          "name" : {
            "type" : "keyword"
          },
          "ip" : {
            "type" : "ip"
          }
        }
      },
      "interval" : {
        "type" : "date"
      },
      "health_evaluation_timestamp" : {
        "type" : "date"
      },
      "health" : {
        "properties" : {
          "status" : {
            "type" : "keyword"
          },
          "score" : {
            "type" : "float"
          },
          "issues" : {
            "type" : "nested",
            "properties" : {
              "metric" : {
                "type" : "keyword"
              },
              "value" : {
                "type" : "float"
              },
              "threshold" : {
                "type" : "float"
              },
              "severity" : {
                "type" : "keyword"
              },
              "message" : {
                "type" : "text"
              }
            }
          },
          "slo" : {
            "properties" : {
              "status" : {
                "type" : "keyword"
              },
              "metrics" : {
                "type" : "nested",
                "properties" : {
                  "name" : {
                    "type" : "keyword"
                  },
                  "value" : {
                    "type" : "float"
                  },
                  "target" : {
                    "type" : "float"
                  },
                  "acceptable" : {
                    "type" : "float"
                  },
                  "status" : {
                    "type" : "keyword"
                  }
                }
              }
            }
          }
        }
      },
      "metadata" : {
        "properties" : {
          "slo_relevant" : {
            "type" : "boolean"
          },
          "metric_category" : {
            "type" : "keyword"
          }
        }
      },
      "kafka" : {
        "properties" : {
          "broker" : {
            "properties" : {
              "request" : {
                "properties" : {
                  "queue" : {
                    "type" : "float"
                  },
                  "time" : {
                    "properties" : {
                      "avg" : {
                        "properties" : {
                          "ms" : {
                            "type" : "float"
                          }
                        }
                      }
                    }
                  }
                }
              },
              "network" : {
                "properties" : {
                  "io" : {
                    "properties" : {
                      "rate" : {
                        "type" : "float"
                      }
                    }
                  }
                }
              },
              "messages" : {
                "properties" : {
                  "in" : {
                    "properties" : {
                      "rate" : {
                        "type" : "float"
                      }
                    }
                  }
                }
              },
              "offline_partition" : {
                "properties" : {
                  "count" : {
                    "type" : "float"
                  }
                }
              },
              "under_replicated_partition" : {
                "properties" : {
                  "count" : {
                    "type" : "float"
                  }
                }
              }
            }
          }
        }
      },
      "mysql" : {
        "properties" : {
          "status" : {
            "properties" : {
              "threads" : {
                "properties" : {
                  "connected" : {
                    "type" : "float"
                  },
                  "running" : {
                    "type" : "float"
                  }
                }
              },
              "slow_queries" : {
                "type" : "float"
              },
              "aborted" : {
                "properties" : {
                  "clients" : {
                    "type" : "float"
                  },
                  "connects" : {
                    "type" : "float"
                  }
                }
              }
            }
          }
        }
      },
      "system" : {
        "properties" : {
          "cpu" : {
            "properties" : {
              "total" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              },
              "iowait" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              }
            }
          },
          "load" : {
            "properties" : {
              "1" : {
                "type" : "float"
              },
              "5" : {
                "type" : "float"
              },
              "15" : {
                "type" : "float"
              }
            }
          },
          "memory" : {
            "properties" : {
              "used" : {
                "properties" : {
                  "pct" : {
                    "type" : "float"
                  }
                }
              },
              "swap" : {
                "properties" : {
                  "used" : {
                    "properties" : {
                      "pct" : {
                        "type" : "float"
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  })
}
