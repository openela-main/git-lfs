%bcond_without check

# https://github.com/git-lfs/git-lfs
%global goipath         github.com/git-lfs/git-lfs
Version:                3.4.1

%gometa

%global gobuilddir %{_builddir}/%{name}-%{version}/_build

Name:           git-lfs
Release:        2%{?dist}
Summary:        Git extension for versioning large files

License:        MIT
URL:            https://git-lfs.github.io/
Source0:        https://github.com/%{name}/%{name}/releases/download/v%{version}/%{name}-v%{version}.tar.gz
Source1:        README.Fedora


# Generated provides by vendor2provides.py
# https://src.fedoraproject.org/rpms/syncthing/blob/603e4e03a92a7d704d199629dd85304018e8279d/f/vendor2provides.py
Provides:       bundled(golang(github.com/alexbrainman/sspi)) = 909beea
Provides:       bundled(golang(github.com/avast/retry-go)) = 2.4.2+incompatible
Provides:       bundled(golang(github.com/davecgh/go-spew)) = 1.1.1
Provides:       bundled(golang(github.com/dpotapov/go-spnego)) = 298b63a
Provides:       bundled(golang(github.com/git-lfs/gitobj/v2)) = 2.1.1
Provides:       bundled(golang(github.com/git-lfs/go-netrc)) = f0c862d
Provides:       bundled(golang(github.com/git-lfs/pktline)) = 06e9096
Provides:       bundled(golang(github.com/git-lfs/wildmatch/v2)) = 2.0.1
Provides:       bundled(golang(github.com/hashicorp/go-uuid)) = 1.0.2
Provides:       bundled(golang(github.com/inconshreveable/mousetrap)) = 1.0.1
Provides:       bundled(golang(github.com/jcmturner/aescts/v2)) = 2.0.0
Provides:       bundled(golang(github.com/jcmturner/dnsutils/v2)) = 2.0.0
Provides:       bundled(golang(github.com/jcmturner/gofork)) = 1.0.0
Provides:       bundled(golang(github.com/jcmturner/goidentity/v6)) = 6.0.1
Provides:       bundled(golang(github.com/jcmturner/gokrb5/v8)) = 8.4.2
Provides:       bundled(golang(github.com/jcmturner/rpc/v2)) = 2.0.3
Provides:       bundled(golang(github.com/leonelquinteros/gotext)) = 1.5.0
Provides:       bundled(golang(github.com/mattn/go-isatty)) = 0.0.4
Provides:       bundled(golang(github.com/olekukonko/ts)) = 78ecb04
Provides:       bundled(golang(github.com/pkg/errors)) = c605e28
Provides:       bundled(golang(github.com/pmezard/go-difflib)) = 1.0.0
Provides:       bundled(golang(github.com/rubyist/tracerx)) = 7879593
Provides:       bundled(golang(github.com/spf13/cobra)) = 1.6.0
Provides:       bundled(golang(github.com/spf13/pflag)) = 1.0.5
Provides:       bundled(golang(github.com/ssgelm/cookiejarparser)) = 1.0.1
Provides:       bundled(golang(github.com/stretchr/testify)) = 1.6.1
Provides:       bundled(golang(github.com/xeipuuv/gojsonpointer)) = 4e3ac27
Provides:       bundled(golang(github.com/xeipuuv/gojsonreference)) = bd5ef7b
Provides:       bundled(golang(github.com/xeipuuv/gojsonschema)) = 6b67b3f
Provides:       bundled(golang(golang.org/x/crypto)) = 7b82a4e
Provides:       bundled(golang(golang.org/x/net)) = 0.7.0
Provides:       bundled(golang(golang.org/x/sync)) = 0.1.0
Provides:       bundled(golang(golang.org/x/sys)) = 0.5.0
Provides:       bundled(golang(golang.org/x/text)) = 0.7.0
Provides:       bundled(golang(gopkg.in/yaml.v3)) = 3.0.1


# Generate man pages
BuildRequires:  /usr/bin/asciidoctor

%if %{with check}
# Tests
BuildRequires:  perl-Digest-SHA
BuildRequires:  perl-Test-Harness
# Tests require full git suite, but not generally needed.
BuildRequires:  git >= 2.32.0
%endif

Requires:       git-core >= 2.32.0

%description
Git Large File Storage (LFS) replaces large files such as audio samples,
videos, datasets, and graphics with text pointers inside Git, while
storing the file contents on a remote server.


%prep
%autosetup -p1 -n %{name}-%{version}

install -m 0755 -vd %{gobuilddir}/bin
install -m 0755 -vd "$(dirname %{gobuilddir}/src/%{goipath})"
ln -fs "$(pwd)" "%{gobuilddir}/src/%{goipath}"

# Modify tests so that they expect binaries where we build them.
sed -i -e 's!\.\./bin/!/%{gobuilddir}/bin/!g' t/Makefile
sed -i -e 's!^BINPATH=.\+!BINPATH="%{gobuilddir}/bin"!g' t/testenv.sh

%build
export GOPATH=%{gobuilddir}:%{gopath}
export GO111MODULE=off

# Build manpages first (some embedding in the executable is done.)
make man GIT_LFS_SHA=unused VERSION=unused PREFIX=unused
pushd docs
%gobuild -o %{gobuilddir}/bin/mangen man/mangen.go
%{gobuilddir}/bin/mangen
popd

%gobuild -o %{gobuilddir}/bin/git-lfs %{goipath}

# Build test executables
pushd %{gobuilddir}/src/%{goipath}
for cmd in t/cmd/*.go; do
    %gobuild -o "%{gobuilddir}/bin/$(basename $cmd .go)" "$cmd"
done
%gobuild -o "%{gobuilddir}/bin/git-lfs-test-server-api" t/git-lfs-test-server-api/*.go
popd

# Remove man pages from docs so they don't get installed twice.
rm -r docs/man


%install
# In Fedora this is done by using %%gopkginstall
install -Dpm0755 %{gobuilddir}/bin/git-lfs %{buildroot}%{_bindir}/%{name}
for section in 1 5 7; do
  install -d -p %{buildroot}%{_mandir}/man${section}/
  install -Dpm0644 man/man${section}/*.${section} %{buildroot}%{_mandir}/man${section}/
done

%post
%{_bindir}/%{name} install --system --skip-repo

%preun
if [ $1 -eq 0 ]; then
    %{_bindir}/%{name} uninstall --system --skip-repo
fi
exit 0


%if %{with check}
%check
%gocheck
PATH=%{buildroot}%{_bindir}:%{gobuilddir}/bin:$PATH \
# https://github.com/git-lfs/git-lfs/issues/5609
# tests fails when running with low level of parallelism
    make -C t PROVE_EXTRA_ARGS="-j40 -v"
%endif


%files
# In Fedora this is done by using %%gopkgfiles 
%doc README.md CHANGELOG.md docs
%license LICENSE.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}*.1*
%{_mandir}/man5/%{name}*.5*
%{_mandir}/man7/%{name}*.7*


%changelog
* Mon Apr 22 2024 Ondřej Pohořelský <opohorel@redhat.com> - 3.4.1-2
- Rebuild with new Golang
- Resolves: RHEL-32570, RHEL-28385, RHEL-28402, RHEL-28432

* Mon Dec 18 2023 Ondřej Pohořelský <opohorel@redhat.com> - 3.4.1-1
- Update to 3.4.1
- Resolves: RHEL-17101

* Thu Jan 05 2023 Ondřej Pohořelský <opohorel@redhat.com> - 3.2.0-1
- Update to 3.2.0
- Resolves: #2139383

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 2.13.3-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 2.13.3-3
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Wed May 05 2021 Ondřej Pohořelský <opohorel@redhat.com> - 2.13.3-2
- Fixed name of source tarball
- Fixed date in the latest changelog entry 
- Related: #1952517

* Thu Apr 22 2021 Ondřej Pohořelský <opohorel@redhat.com> - 2.13.3-1
- Update to latest version
- Resolves: #1952517

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 2.13.0-2
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Jan 06 2021 Ondřej Pohořelský <opohorel@redhat.com> - 2.13.0-1
- Enable bundling
- Update to latest version

* Mon Nov 09 2020 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.12.1-1
- Update to latest version (#1894780)

* Thu Sep 03 2020 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.12.0-1
- Update to latest version (#1874604)
- Remove duplicate docs/man directory (#1852765)
- Add an option to disable modifying the git filter config (#1768060)

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.11.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.11.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun May 10 2020 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.11.0-1
- Update to latest version

* Thu Feb 20 2020 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.10.0-1
- Update to latest version

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Jan 07 2020 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.9.2-1
- Update to latest version

* Wed Jan 01 2020 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.9.0-1
- Update to latest version

* Fri Aug 30 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.8.0-4
- Customize vendor information in version

* Fri Aug 30 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.8.0-3
- Update to latest version

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.7.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Jul 10 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.7.2-2
- Update to latest Go macros

* Wed Apr 24 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.7.2-1
- Update to latest version

* Wed Feb 27 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.7.1-1
- Update to latest version

* Thu Feb 21 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.7.0-1
- Update to latest version

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.6.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Tue Jan 15 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.6.1-1
- Update to latest version

* Mon Jan 14 2019 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.5.2-4
- Rebuilt for dependencies

* Tue Oct 23 2018 Nicolas Mailhot <nim@fedoraproject.org>
- 2.5.2-3
- redhat-rpm-config-123 triggers bugs in gosetup, remove it from Go spec files as it’s just an alias
- https://lists.fedoraproject.org/archives/list/devel@lists.fedoraproject.org/message/RWD5YATAYAFWKIDZBB7EB6N5DAO4ZKFM/

* Fri Oct 12 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.5.2-2
- rebuilt

* Wed Oct 10 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.5.2-1
- Update to latest version

* Tue Sep 04 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.5.1-1
- Update to latest version

* Mon Sep 03 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.5.0-1
- Update to 2.5.0

* Wed Aug 29 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.4.2-1
- Update to 2.4.2

* Tue Jul 31 2018 Florian Weimer <fweimer@redhat.com> - 2.4.1-3
- Rebuild with fixed binutils

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed May 23 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.4.1-1
- Update to latest release

* Mon May 21 2018 Carl George <carl@george.computer> - 2.4.0-3
- Fix %%preun to correctly remove the lfs filter on uninstall (rhbz#1580357)

* Mon Mar 12 2018 Carl George <carl@george.computer> - 2.4.0-2
- Add %%go_arches fallback to work around Koji issues

* Sun Mar 04 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.4.0-1
- Update to latest release.

* Thu Feb 08 2018 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-6
- Add patches to build with Go 1.10.

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.3.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Mon Dec 04 2017 Carl George <carl@george.computer> - 2.3.4-4
- Use vendored libraries on RHEL
- Skip test on RHEL
- Don't build man pages on RHEL due to missing ronn
- Don't build html versions of man pages

* Fri Dec 01 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-3
- Require git-core instead of git.

* Fri Nov 03 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-2
- Patch tests to work on slow systems like arm and aarch builders.
- Fix "git lfs help" command.

* Fri Nov 03 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.3.4-1
- Update to latest release.
- Run all tests during build.

* Fri Sep 01 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.2.1-3
- Remove redundant doc tag on manpages.
- Use path macros in %%post/%%postun.

* Thu Aug 31 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.2.1-2
- Disable unnecessary subpackages.

* Sun Jul 30 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.2.1-1
- Update to latest version.

* Wed Apr 19 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.2-2
- Patch up to build with Go 1.7

* Wed Apr 19 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.2-1
- Update to latest release
- Add some requested macros

* Tue Mar 14 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.1-1
- Update to latest release
- Don't disable git-lfs globally during upgrade

* Mon Mar 06 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 2.0.0-1
- Update to latest release

* Sun Feb 12 2017 Elliott Sales de Andrade <quantum.analyst@gmail.com> - 1.5.5-1
- Update to latest release
- Add -devel and -unit-test-devel subpackages
- Add post/preun scriptlets for global enablement

* Sun May 15 2016 Igor Gnatenko <i.gnatenko.brain@gmail.com> - 1.2.0-1
- Initial package
