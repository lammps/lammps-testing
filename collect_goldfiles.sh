#!/bin/bash
find tests -iname log.*.linux* | tar -cvzf goldfiles.tar.gz -T -
