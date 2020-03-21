# Tamper-Proof Broadcast

## Installation

## Usage

## Tests

## Benchmarks

## Design
The architecture consists of three layers:
- The application layer
- The tamper-proof broadcast layer (or, blockchain interaction layer)
- The blockchain layer

```
------------------------------------------------------
| application                                        |
------------------------------------------------------
                          ^
------------------------------------------------------
| tamper-proof broadcast protocol:                   |
| FIFO-order reliable tamper-proof broadcast         |
| or                                                 |
| total-order reliable tamper-proof broadcast        |
| or                                                 |
| high-throughput low-latency tamper-proof broadcast |
------------------------------------------------------
                          ^
------------------------------------------------------
| blockchain                                         |
------------------------------------------------------
```

## Development
- Format source code: `black *`
- Generate requirements: `pipreqs . --force`
