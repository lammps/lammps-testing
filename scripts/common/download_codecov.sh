#!/bin/bash

curl -fLso codecov https://codecov.io/bash

VERSION=$(grep -o 'VERSION=\"[0-9\.]*\"' codecov | cut -d'"' -f2);

for i in 1 256 512
do
    shasum -a $i -c <(curl -s "https://raw.githubusercontent.com/codecov/codecov-bash/${VERSION}/SHA${i}SUM" | grep -w "codecov")
done
