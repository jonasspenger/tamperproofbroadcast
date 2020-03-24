# Tamper-Proof Broadcast Docker Container
Docker container for repository at github.com/jonasspenger/tamperproofbroadcast

## Build
```
docker build \
  -t tamperproofbroadcast \
  .;
```

## Run
```
docker run \
  --rm \
  -p=3489:3489 \
  -p=3490:3490 \
  tamperproofbroadcast;
```

## Or, run and enter shell
```
docker run \
  -it \
  --rm \
  tamperproofbroadcast \
  /bin/ash;
```

## Or, run from docker hub image
```
docker run \
  --rm \
  -p=3489:3489 \
  -p=3490:3490 \
  jonasspenger/tamperproofbroadcast;
```
