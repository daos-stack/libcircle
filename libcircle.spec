%global with_mpich 1
%if (0%{?rhel} >= 8)
%global with_openmpi 1
%global with_openmpi3 0
%else
%global with_openmpi 0
%global with_openmpi3 1
%endif

%if (0%{?suse_version} >= 1500)
%global module_load() if [ "%{1}" == "openmpi3" ]; then MODULEPATH=/usr/share/modules module load gnu-openmpi; else MODULEPATH=/usr/share/modules module load gnu-%{1}; fi
%else
%global module_load() module load mpi/%{1}-%{_arch}
%endif

%if %{with_mpich}
%global mpi_list mpich
%endif
%if %{with_openmpi}
%global mpi_list %{?mpi_list} openmpi
%endif
%if %{with_openmpi3}
%if 0%{?fedora}
# this would be nice to use but causes issues with linting
# since that is done on Fedora
#{error: openmpi3 doesn't exist on Fedora}
%endif
%global mpi_list %{?mpi_list} openmpi3
%endif

%if (0%{?suse_version} >= 1500)
%global mpi_libdir %{_libdir}/mpi/gcc
%global mpi_lib_ext lib64
%global mpi_includedir %{_libdir}/mpi/gcc
%global mpi_include_ext /include
%else
%global mpi_libdir %{_libdir}
%global mpi_lib_ext lib
%global mpi_includedir  %{_includedir}
%global mpi_include_ext -%{_arch}
%endif

%global maj_ver 0.3

Name:    libcircle
Version: %{maj_ver}.0
Release: 4%{?dist}

License: BSD
URL: http://hpc.github.io/libcircle/
Source: https://github.com/hpc/%{name}/releases/download/v%{maj_ver}/%{name}-%{version}.tar.gz
Summary: A library used to distribute workloads
%if (0%{?suse_version} >= 1500)
BuildRequires: lua-lmod
%else
BuildRequires: Lmod
%endif
BuildRequires:  check-devel
BuildRequires:  doxygen
BuildRequires:  graphviz

%description
A simple interface for processing workloads using an automatically
distributed global queue.

%if %{with_openmpi}
%package openmpi
Summary:        Libcircle Open MPI libraries
BuildRequires:  openmpi-devel

%description openmpi
A simple interface for processing workloads using an automatically
distributed global queue.

libcircle compiled with Open MPI


%package openmpi-devel
Summary:    Development headers and libraries for Open MPI libcircle
Requires:   %{name}-openmpi%{?_isa} = %{version}-%{release}

%description openmpi-devel
A simple interface for processing workloads using an automatically
distributed global queue.

This package contains development headers and libraries for Open
MPI ibcircle
%endif

%if %{with_openmpi3}
%package openmpi3
Summary:        Libcircle Open MPI libraries
BuildRequires:  openmpi3-devel

%description openmpi3
A simple interface for processing workloads using an automatically
distributed global queue.

libcircle compiled with Open MPI

%if (0%{?suse_version} >= 1500)
%package -n libcircle2-openmpi3
Summary: Light-weight Group Library for MPI process groups -- Shared libraries
Obsoletes: libcircle2

%description -n libcircle2-openmpi3
Shared libraries for %{name}-openmpi3.
%endif

%package openmpi3-devel
Summary:    Development headers and libraries for Open MPI libcircle
%if (0%{?suse_version} >= 1500)
Requires: libcircle2-openmpi3%{_isa} = %version-%release
%else
Requires:   %{name}-openmpi3%{?_isa} = %{version}-%{release}
%endif

%description openmpi3-devel
A simple interface for processing workloads using an automatically
distributed global queue.

This package contains development headers and libraries for Open
MPI ibcircle
%endif

%if %{with_mpich}
%package mpich
Summary:        Libcircle MPICH libraries
BuildRequires:  mpich-devel

%description mpich
A simple interface for processing workloads using an automatically
distributed global queue.

libcircle compiled with MPICH

%if (0%{?suse_version} >= 1500)
%package -n libcircle2-mpich
Summary: Light-weight Group Library for MPI process groups -- Shared libraries
Obsoletes: libcircle2

%description -n libcircle2-mpich
Shared libraries for %{name}-mpich.
%endif

%package mpich-devel
Summary:    Development headers and libraries for MPICH libcircle
%if (0%{?suse_version} >= 1500)
Requires: libcircle2-mpich%{_isa} = %version-%release
%else
Requires:   %{name}-mpich%{?_isa} = %{version}-%{release}
%endif

%description mpich-devel
A simple interface for processing workloads using an automatically
distributed global queue.

This package contains development headers and libraries for
MPICH libcircle
%endif

%prep
%setup -q

%build
%global _configure ../configure
export CC=mpicc
for mpi in %{?mpi_list}; do
  mkdir $mpi
  pushd $mpi
  %module_load $mpi
  %configure --enable-doxygen --enable-tests --disable-static --includedir=%{mpi_includedir}/$mpi%{mpi_include_ext} --libdir=%{mpi_libdir}/$mpi/%{mpi_lib_ext}
  %make_build
  module purge
  popd
done

%install
for mpi in %{?mpi_list}; do
  %module_load $mpi
  %make_install -C $mpi
  rm %{buildroot}/%{mpi_libdir}/$mpi/%{mpi_lib_ext}/*.la
  module purge
done

%check
for mpi in %{?mpi_list}; do
  %module_load $mpi
  %make_install -C $mpi
  if ! make -C $mpi check; then
    cat $mpi/tests/test-suite.log
    exit 1
  fi
  rm %{buildroot}/%{mpi_libdir}/$mpi/%{mpi_lib_ext}/*.la
  module purge
done

%if %{with_openmpi}
%files openmpi
%license COPYING
%doc AUTHORS
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/%{name}.so.*

%files openmpi-devel
%{mpi_includedir}/openmpi%{mpi_include_ext}/%{name}.h
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/%{name}.so
%{mpi_libdir}/openmpi/%{mpi_lib_ext}/pkgconfig/%{name}.pc
%endif

%if %{with_openmpi3}
%files openmpi3
%license COPYING
%doc AUTHORS
%if (0%{?suse_version} >= 1500)
%files -n libcircle2-openmpi3
%endif
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/%{name}.so.*

%files openmpi3-devel
%{mpi_includedir}/openmpi3%{mpi_include_ext}/%{name}.h
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/%{name}.so
%{mpi_libdir}/openmpi3/%{mpi_lib_ext}/pkgconfig/%{name}.pc
%endif

%if %{with_mpich}
%files mpich
%license COPYING
%doc AUTHORS
%if (0%{?suse_version} >= 1500)
%files -n libcircle2-mpich
%endif
%{mpi_libdir}/mpich/%{mpi_lib_ext}/%{name}.so.*

%files mpich-devel
%{mpi_includedir}/mpich%{mpi_include_ext}/%{name}.h
%{mpi_libdir}/mpich/%{mpi_lib_ext}/%{name}.so
%{mpi_libdir}/mpich/%{mpi_lib_ext}/pkgconfig/%{name}.pc
%endif

%changelog
* Mon May 17 2021 Brian J. Murrell <brian.murrell@intel.com> - 0.3.0-4
- Package for openmpi on EL8

* Tue Sep 29 2020 Brian J. Murrell <brian.murrell@intel.com> - 0.3.0-3
- Obsoletes libcircle2 on SUSE since they package their own older
  version built with just openmpi2

* Tue Sep 29 2020 Brian J. Murrell <brian.murrell@intel.com> - 0.3.0-2
- Package for multiple MPI stacks and multiple distros

* Mon Sep 21 2020 John E. Malmberg <john.e.malmberg@intel.com> - 0.3.0-1
- Use openmpi3 instead of openmpi, add environment-modules depend.

* Sat Feb 01 2020 Christoph Junghans <junghans@votca.org> - 0.3-3
- Remove s390x workaround

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jan 23 2020 Christoph Junghans <junghans@votca.org> - 0.3-1
- Version bump to 0.3 (bug #1794592)

* Fri Jan 17 2020 Jeff Law <law@redhat.com> - 0.2.1-0.9rc1
- Redefine _configure and use standard #configure macro

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-0.8rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Feb 14 2019 Orion Poplawski <orion@nwra.com> - 0.2.1-0.7rc1
- Rebuild for openmpi 3.1.3

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-0.6rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-0.5rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.1-0.4rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Tue Dec 05 2017 Christoph Junghans <junghans@votca.org> - 0.2.1-0.3rc1
- Comments from #1513733

* Wed Nov 15 2017 Christoph Junghans <junghans@votca.org> - 0.2.1-0.2rc1
- Split devel pacakge

* Wed Nov 15 2017 Christoph Junghans <junghans@votca.org> - 0.2.1-0.1rc1
- First release.
