%if 0%{?fedora} || 0%{?rhel} == 6
%global with_devel 1
%global with_bundled 0
%global with_debug 1
%global with_check 1
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%define copying() \
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7 \
%license %{*} \
%else \
%doc %{*} \
%endif

%global provider        github
%global provider_tld    com
%global project         BurntSushi
%global repo            toml
# https://github.com/BurntSushi/toml
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          2ceedfee35ad3848e49308ab0c9a4f640cfb5fb2
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           golang-%{provider}-%{project}-%{repo}
Version:        0
Release:        0.4.git%{shortcommit}%{?dist}
Summary:        TOML parser and encoder for Go with reflection
License:        BSD
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz
Provides:       tomlv = %{version}-%{release}

# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
%endif

Provides:      golang(%{import_path}) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_arches not defined fall through to implicit golang archs
%if 0%{?go_arches:1}
ExclusiveArch:  %{go_arches}
%else
ExclusiveArch:   %{ix86} x86_64 %{arm}
%endif
# If gccgo_arches does not fit or is not defined fall through to golang
%ifarch 0%{?gccgo_arches}
BuildRequires:   gcc-go >= %{gccgo_min_vers}
%else
BuildRequires:   golang
%endif

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build
%if 0%{?with_debug}
function gobuild { go build -a -ldflags "-B 0x$(head -c20 /dev/urandom|od -An -tx1|tr -d ' \n')" -v -x "$@"; }
%else
function gobuild { go build -a "$@"; }
%endif

mkdir -p _build/src/github.com/BurntSushi
ln -sf $(pwd) _build/src/github.com/BurntSushi/toml
export GOPATH=$(pwd)/_build:%{gopath}
cd cmd/tomlv
gobuild .

%install
# source codes for building projects
%if 0%{?with_devel}
install -d %{buildroot}/%{_bindir}
install -p -m 755 ./cmd/tomlv/tomlv %{buildroot}%{_bindir}/tomlv
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *.go but no *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%ifarch 0%{?gccgo_arches}
function gotest { %{gcc_go_test} "$@"; }
%else
%if 0%{?golang_test:1}
function gotest { %{golang_test} "$@"; }
%else
function gotest { go test "$@"; }
%endif
%endif

export GOPATH=%{buildroot}/%{gopath}:%{gopath}
gotest %{import_path}
%endif

%files
%{_bindir}/tomlv

%if 0%{?with_devel}
%files devel -f devel.file-list
%copying COPYING README.md
%doc README.md
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%dir %{gopath}/src/%{import_path}
%endif

%if 0%{?with_unit_test}
%files unit-test -f unit-test.file-list
%copying COPYING
%doc README.md
%endif

%changelog
* Tue Jul 28 2015 Fridolin Pokorny <fpokorny@redhat.com> - 0-0.4.git2ceedfe
- Update of spec file to spec-2.0
  resolves: #1247656

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.4.git2ceedfe
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Oct 23 2014 jchaloup <jchaloup@redhat.com> - 0-0.3.git2ceedfe
- Bump to upstream 2ceedfee35ad3848e49308ab0c9a4f640cfb5fb2
- spec file polishing to follow go draft
  related: #1120865

* Mon Sep 22 2014 jchaloup <jchaloup@redhat.com> - 0-0.2.gitbd2bdf7
- do not own golang directories
- defattr and attr not needed

* Mon Sep 22 2014 jchaloup <jchaloup@redhat.com> - 0-0.1.gitbd2bdf7
- accomodated changes from Vincent Batts
- gopath is in the rpm macros, and set exclusive arch too, to prevent s390 builds
- move the buildarch noarch to the devel, since it is source only
- preserve timestamps of source copied and as an added perk
- the tomlv command provided in this project is useful for validating *.toml files
- go test

* Thu Jul 17 2014 Colin Walters <walters@verbum.org>
- Initial package
