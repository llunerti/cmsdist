### RPM external sherpa 2.2.11
%define tag 600078cc741021be898f15563235cf6c809ca5ff
%define branch cms/v%realversion
%define github_user cms-externals
Source: http://www.hepforge.org/archive/sherpa/SHERPA-MC-%{realversion}.tar.gz
Requires: hepmc lhapdf blackhat sqlite fastjet openssl scons python openmpi rivet
BuildRequires: mcfm swig autotools
Patch0: sherpa-2.2.10-hepmcshort

%ifos linux
%ifnarch ppc64le
Requires: openloops
%endif
%endif

%prep
%setup -q -n SHERPA-MC-%{realversion}

autoreconf -i --force

# Force architecture based on %%cmsplatf
case %cmsplatf in
  *_amd64_gcc*) ARCH_CMSPLATF="-m64" ;;
esac

case %cmsplatf in
  osx*)
    perl -p -i -e 's|-rdynamic||g' \
      configure \
      AddOns/Analysis/Scripts/Makefile.in
  ;;
esac

%patch0 -p1

%build
./configure --prefix=%i --enable-analysis --disable-silent-rules \
            --enable-fastjet=$FASTJET_ROOT \
            --enable-hepmc2=$HEPMC_ROOT \
            --enable-rivet=$RIVET_ROOT \
            --enable-lhapdf=$LHAPDF_ROOT \
            --enable-blackhat=$BLACKHAT_ROOT \
            --enable-pyext \
            --enable-ufo \
            ${OPENLOOPS_ROOT+--enable-openloops=$OPENLOOPS_ROOT} \
            --enable-mpi \
            --with-sqlite3=$SQLITE_ROOT \
            --enable-analysis \
            CC="mpicc" \
            CXX="mpicxx" \
            MPICXX="mpicxx" \
            FC="mpifort" \
            CXXFLAGS="-fuse-cxa-atexit $ARCH_CMSPLATF -O2 -std=c++0x -I$LHAPDF_ROOT/include -I$BLACKHAT_ROOT/include -I$OPENSSL_ROOT/include -I$RIVET_ROOT/include" \
            LDFLAGS="-ldl -L$BLACKHAT_ROOT/lib/blackhat -L$QD_ROOT/lib -L$OPENSSL_ROOT/lib"

make %{makeprocesses}

%install
make install
find %{i}/lib -name '*.la' -delete
sed -i -e 's|^#!/.*|#!/usr/bin/env python|' %{i}/bin/Sherpa-generate-model

%post
%{relocateConfig}lib/python2.7/site-packages/ufo_interface/sconstruct_template
%{relocateConfig}bin/make2scons
%{relocateConfig}share/SHERPA-MC/makelibs
%{relocateConfig}bin/Sherpa-config
%{relocateConfig}bin/Sherpa-generate-model
%{relocateConfig}include/SHERPA-MC/ATOOLS/Org/CXXFLAGS.H
