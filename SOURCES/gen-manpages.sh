# As `ronn` package has not been packaged for RHEL7 yet, man pages need to be generated on Fedora when rebasing to a new version as follows:

# Pass package version(eg. `2.4.1`) as argument

VERSION=$1

cd git-lfs-$VERSION/docs

ronn --roff man/*.ronn

cd ..

tar -czvf manpages.tgz docs/man/*.{1,5}

cp manpages.tgz ../

