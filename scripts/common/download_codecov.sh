#!/bin/bash

curl -fLso codecov https://codecov.io/bash

VERSION=$(grep -o 'VERSION=\"[0-9\.]*\"' codecov | cut -d'"' -f2);

# hack to work around issue with 1.0.4 release
if [ ${VERSION} = 1.0.3 ]
then
        VERSION=1.0.4
fi

# redownload to make certain we have consistent files
rm -f codecov
curl -fLso codecov https://raw.githubusercontent.com/codecov/codecov-bash/${VERSION}/codecov

for i in 1 256 512
do
    shasum -a $i -c <(curl -s "https://raw.githubusercontent.com/codecov/codecov-bash/${VERSION}/SHA${i}SUM" | grep -w "codecov")
done
