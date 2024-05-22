# As `asciidoctor` package has not been packaged to RHEL 8:

# Pass package version(eg. `3.4.0`) as argument

VERSION=$1

cd git-lfs-$VERSION

make man GIT_LFS_SHA=unused VERSION=unused PREFIX=unused
rm -r man/html

tar -czvf manpages.tgz man/*

cp manpages.tgz ../

