Summary:	Spin down idle [USB] hard disks
Name:		hd-idle
Version:	1.05
Release:	1
License:	GPL v2
Group:		Applications/System
Source0:	http://downloads.sourceforge.net/hd-idle/%{name}-%{version}.tgz
# Source0-md5:	5fa72fe717bc80011a79d6740d2903f3
Source1:	%{name}.service
Source2:	%{name}.logrotate
URL:		http://hd-idle.sourceforge.net
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
hd-idle is a utility program for spinning-down external disks after a
period of idle time. Since most external IDE disk enclosures don't
support setting the IDE idle timer, a program like hd-idle is required
to spin down idle disks automatically.

A word of caution: hard disks don't like spinning up too often. Laptop
disks are more robust in this respect than desktop disks but if you
set your disks to spin down after a few seconds you may damage the
disk over time due to the stress the spin-up causes on the spindle
motor and bearings. It seems that manufacturers recommend a minimum
idle time of 3-5 minutes, the default in hd-idle is 10 minutes.

One more word of caution: hd-idle will spin down any disk accessible
via the SCSI layer (USB, IEEE1394, ...) but it will not work with real
SCSI disks because they don't spin up automatically. Thus it's not
called scsi-idle and I don't recommend using it on a real SCSI system
unless you have a kernel patch that automatically starts the SCSI
disks after receiving a sense buffer indicating the disk has been
stopped. Without such a patch, real SCSI disks won't start again and
you can as well pull the plug.

%prep
%setup -q -n %{name}
%{__sed} -i 's/install -D -g root -o root/install -D/' Makefile

%build
%{__make} \
	CC="%{__cc}" \
	CFLAGS="%{rpmcppflags} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}"

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{systemdunitdir}
install -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
echo 'HD_IDLE_OPTS="-i 1200 -l %{_localstatedir}/log/hd-idle/hd-idle.log"' > \
     $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
install -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_reload

%files
%defattr(644,root,root,755)
%doc README
%defattr(644,root,root,755)
%attr(755,root,root) %{_sbindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{systemdunitdir}/%{name}.service
%config(noreplace) /etc/logrotate.d/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%dir %{_localstatedir}/log/%{name}
