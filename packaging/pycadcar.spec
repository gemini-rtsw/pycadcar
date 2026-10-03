# pycadcar: the pygeminirec package -- Gemini apply/CAD/CAR records for caproto
# IOCs -- for EL9's system Python 3.9, which the GNIRS DC image runs.
#
# caproto itself is not packaged for EL9, so it is deliberately not a Requires;
# the image that runs the IOC installs it with pip.

%global specver 0.1.0
# $GIT_HASH first: build_rpm.sh computes it on the host and passes it in.
%define git_hash %(if [ -n "$GIT_HASH" ]; then echo "$GIT_HASH"; else git rev-parse --short HEAD 2>/dev/null || echo nogit; fi)

Name:           pycadcar
Version:        %{specver}
Release:        1.git%{git_hash}%{?dist}
Summary:        Gemini apply/CAD/CAR records for caproto (pygeminirec), Python 3.9
License:        Proprietary
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3
BuildRequires:  python3-setuptools
BuildRequires:  python3-rpm-macros
Requires:       python3

%description
pygeminirec implements the Gemini apply, CAD and CAR records on top of the
caproto IOC framework. Installed into the Python 3.9 site-packages.

%prep
%setup -q

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --skip-build --root %{buildroot} --prefix /usr

%check
PYTHONPATH=%{buildroot}%{python3_sitelib} %{__python3} -c "import pygeminirec"

%files
%{python3_sitelib}/pygeminirec
%{python3_sitelib}/pygeminirec-*.egg-info

%changelog
* Fri Oct 02 2026 Hawi Stecher <hawi.stecher@noirlab.edu> - 0.1.0-1
- Initial packaging for gemini-rtsw-ci, EL9.
