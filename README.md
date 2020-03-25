# Tamper-Proof Broadcast

## Installation

## Usage

## Tests
Run all integration tests:
```
python3 -m unittest discover tests/integrationtests -v
```

Run specific test:
```
python3 -m unittest tests.integrationtests.test_fotb -v
python3 -m unittest tests.integrationtests.test_totb -v
python3 -m unittest tests.integrationtests.test_htlltb -v
python3 -m unittest tests.integrationtests.test_htlltbtest -v
```

## Benchmarks
Runs a broadcast and deliver workload for a set duration, and saves results to a file.
If google storage bucket name is set, it is also uploaded there.
```
python3 tests/benchmarks/benchmark.py -h
python3 tests/benchmarks/benchmark.py fotb -h
python3 tests/benchmarks/benchmark.py totb -h
python3 tests/benchmarks/benchmark.py htlltb -h
python3 tests/benchmarks/benchmark.py htlltbtest -h
```

Run all benchmarks for a duration of 60 seconds:
```
python3 tests/benchmarks/benchmark.py --benchmark-duration=60 --benchmark-testid=test-0 fotb --multichain-create=True
python3 tests/benchmarks/benchmark.py --benchmark-duration=60 --benchmark-testid=test-1 totb --multichain-create=True
python3 tests/benchmarks/benchmark.py --benchmark-duration=60 --benchmark-testid=test-2 htlltb --etcd-create=True --multichain-create=True
python3 tests/benchmarks/benchmark.py --benchmark-duration=60 --benchmark-testid=test-3 htlltbtest --etcd-create=True
```

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
