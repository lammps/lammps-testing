#!/bin/bash

VERSION=1.0.5

rm -f codecov
curl -fLso codecov https://github.com/codecov/codecov-bash/releases/download/${VERSION}/codecov

for i in 1 256 512
do
    rm -f SHA${i}SUM
    curl -fLso SHA${i}SUM https://github.com/codecov/codecov-bash/releases/download/${VERSION}/SHA${i}SUM
    grep -w 'codecov' SHA${i}SUM | shasum -a $i -c -
done
