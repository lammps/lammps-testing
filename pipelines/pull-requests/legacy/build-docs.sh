export LC_ALL=C
echo "Generate HTML"
make -C doc clean-all
make -C doc -j 8 html

cd doc/html
tar cvzf ../lammps-docs.tar.gz *
cd ../..

export LC_ALL=C
echo "Generate PDF"
make -C doc pdf

export LC_ALL=C
echo "Do spellcheck"
make -C doc -j 8 spelling
#echo ${USER}-${PWD} | python utils/sha1sum.py
#cp -R /tmp/lammps-docs-ebe2ec56ed1854589319120dbd8bd0e816d30813/rst/ .
