%bcond_without headers_more
%bcond_without upstream_fair
%bcond_without with_ipv6

%bcond_with balancer
%bcond_with perl_module
%bcond_with file_aio
%bcond_with extended_stats
%bcond_with ustats
%bcond_with chunkin

# from f20 src rpm
%global  _hardened_build     1

%global nginx_user      nginx
%global nginx_group     %{nginx_user}
%global nginx_home      %{_localstatedir}/lib/nginx
%global nginx_home_tmp  %{nginx_home}/tmp
%global nginx_logdir    %{_localstatedir}/log/nginx
%global nginx_confdir   %{_sysconfdir}/nginx
%global nginx_datadir   %{_datadir}/nginx
%global nginx_webroot   %{nginx_datadir}/html

# gperftools exist only on selected arches
%ifarch %{ix86} x86_64 ppc ppc64 %{arm}
%global  with_gperftools     0
%endif

Name:           nginx
Version:        1.4.1
%if %{with balancer}
Release:        0.balancer.SS%{?dist}
%else
%if %{with upstream_fair}
Release:        0.fair.SS%{?dist}
%else
Release:        0.SS%{?dist}
%endif
%endif
Epoch:          128
Summary:        Robust, small and high performance HTTP and reverse proxy server
Group:          System Environment/Daemons

# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:        BSD
URL:            http://nginx.net/
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{with file_aio}
# This is for the aio support and fixes
Conflicts:          kernel < 2.6.18-224.el5
%endif
%if 0%{?with_gperftools}
BuildRequires:     gperftools-devel
%endif
BuildRequires:      pcre-devel,perl-devel,zlib-devel,openssl-devel
%if %{with perl_module}
BuildRequires:      perl(ExtUtils::Embed)
Requires:           perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%endif
BuildRequires:      libxslt-devel,GeoIP-devel,gd-devel
# for /usr/sbin/useradd
Requires(pre):      shadow-utils
Requires(post):     chkconfig
# for /sbin/service
Requires(preun):    chkconfig, initscripts
Requires(postun):   initscripts
Provides:           webserver
Requires:          GeoIP
Requires:          gd
Requires:          openssl
Requires:          pcre


Source0:    http://nginx.org/download/nginx-%{version}.tar.gz
Source1:    %{name}.init
Source2:    %{name}.logrotate
Source3:    virtual.conf
Source4:    ssl.conf
Source5:    %{name}.sysconfig
Source6:    nginx.conf
Source100:  index.html
Source101:  poweredby.png
Source102:  nginx-logo.png
Source103:  50x.html
Source104:  404.html
Source105:  nginx_custom_configs_htmlroot.tar.gz

# Third party modules
Source1000: https://github.com/gnosek/nginx-upstream-fair/tarball/2131c731d00b49c6ac0106495817b79b5d74aab8/gnosek-nginx-upstream-fair-2131c73.tar.gz
Source1001: https://github.com/agentzh/chunkin-nginx-module/tarball/v0.22rc1/agentzh-chunkin-nginx-module-v0.22rc1-0-gb0a3ee3.tar.gz
Source1002: https://github.com/agentzh/headers-more-nginx-module/tarball/v0.14/agentzh-headers-more-nginx-module-v0.14-0-g2cbbc15.tar.gz
Source1003: https://github.com/ry/nginx-ey-balancer/tarball/v0.0.6/ry-nginx-ey-balancer-v0.0.6-7-g467df3f.tar.gz
#Source1004: https://download.github.com/cep21-healthcheck_nginx_upstreams-b33a846.tar.gz
#Source1005:  https://download.github.com/ngx_supervisord-1.4.tar.gz
#Source1006:  http://ustats.googlecode.com/svn/trunk/ustats.tar.gz
Source1006:  ustats-rev35.tar.gz
Source1007:   https://github.com/zealot83/ngx_http_extended_status_module/tarball/gh-pages/zealot83-ngx_http_extended_status_module-9c2cd0b.tar.gz

Source1111 https://download.ssabchew.info/nginx_custom_configs_htmlroot.tar.gz

# removes -Werror in upstream build scripts.  -Werror conflicts with
# -D_FORTIFY_SOURCE=2 causing warnings to turn into errors.
Patch0:     nginx-auto-cc-gcc.patch
Patch1:     nginx-ey-balancer.patch
Patch2:     request_start_variable.patch
#Patch2:     https://gist.github.com/michaeldauria/2890138/raw/ee28dd97de0a0c4a2762b3de2810c55c1fd943bf/request_start_variable.patch
Patch3:     nginx-ey-balancer-1.2.patch
#Patch4:     nginx-http_healthcheck.patch

%description
Nginx is a web server and a reverse proxy server for HTTP, SMTP, POP3 and
IMAP protocols, with a strong focus on high concurrency, performance and low
memory usage.


%prep
%if %{with balancer} && %{with upstream_fair}
echo 'Please select only one of balancer and upstream_fair'
false
%endif

%setup -q
cp  %{SOURCE105} .
tar zxf %{SOURCE105}

# Move here all modules?
# Patch 3 have to patch a module, so we uncompress it here.
%if %{with balancer}
mkdir balancer
tar -C balancer -xzf "%{SOURCE1003}"
mv balancer/*/* balancer/
%endif

%patch0 -p0

%if %{with balancer}
%patch1 -p0
%endif

%patch2 -p0

%if %{with balancer}
%patch3 -p0
%endif
#%patch4 -p0

%build
%if %{with upstream_fair}
mkdir upstream_fair
tar -C upstream_fair -xzf "%{SOURCE1000}"
mv upstream_fair/*/* upstream_fair/
%endif

%if %{with chunkin}
mkdir chunkin
tar -C chunkin -xzf "%{SOURCE1001}"
mv chunkin/*/* chunkin/
%endif

%if %{with headers_more}
mkdir headers_more
tar -C headers_more -xzf "%{SOURCE1002}"
mv headers_more/*/* headers_more/
%endif

%if %{with ustats}
tar -xzf "%{SOURCE1006}"
mv ustats/*/* ustats/
patch -p1 -i  ustats/nginx.patch
%endif

%if %{with extended_status}
mkdir extended_status
tar -C extended_status -xzf "%{SOURCE1007}"
mv extended_status/*/* extended_status/
patch -p1 -i  extended_status/extended_status-1.0.11.patch
%endif

#mkdir healthcheck
#tar -C healthcheck -zxf "%{SOURCE1004}"
#mv healthcheck/*/* healthcheck/

#mkdir ngx_supervisord
#tar -C ngx_supervisord -zxf "%{SOURCE1005}"
#mv ngx_supervisord/*/* ngx_supervisord/

# nginx does not utilize a standard configure script.  It has its own
# and the standard configure options cause the nginx configure script
# to error out.  This is is also the reason for the DESTDIR environment
# variable.  The configure script(s) have been patched (Patch1 and
# Patch2) in order to support installing into a build environment.
export DESTDIR=%{buildroot}
./configure \
    --prefix=%{nginx_datadir} \
    --sbin-path=%{_sbindir}/%{name} \
    --conf-path=%{nginx_confdir}/%{name}.conf \
    --error-log-path=%{nginx_logdir}/error.log \
    --http-log-path=%{nginx_logdir}/access.log \
    --http-client-body-temp-path=%{nginx_home_tmp}/client_body \
    --http-proxy-temp-path=%{nginx_home_tmp}/proxy \
    --http-fastcgi-temp-path=%{nginx_home_tmp}/fastcgi \
    --http-uwsgi-temp-path=%{nginx_home_tmp}/uwsgi \
    --http-scgi-temp-path=%{nginx_home_tmp}/scgi \
    --pid-path=%{_localstatedir}/run/%{name}.pid \
    --lock-path=%{_localstatedir}/lock/subsys/%{name} \
    --user=%{nginx_user} \
    --group=%{nginx_group} \
    --with-http_ssl_module \
    --with-http_spdy_module \
    --with-http_realip_module \
    --with-http_addition_module \
    --with-http_xslt_module \
    --with-http_image_filter_module \
    --with-http_geoip_module \
    --with-http_sub_module \
    --with-http_dav_module \
    --with-http_flv_module \
    --with-http_mp4_module \
    --with-http_gunzip_module \
    --with-http_gzip_static_module \
    --with-http_random_index_module \
    --with-http_secure_link_module \
    --with-http_degradation_module \
    --with-http_stub_status_module \
    --with-mail \
    --with-mail_ssl_module \
%if %{with extended_stats}
    --add-module="$PWD/extended_status/addons" \
%endif
%if %{with ustats}
    --add-module="$PWD/ustats" \
%endif
%if %{with file_aio}
    --with-file-aio \
%endif
%if %{with upstream_fair}
    --add-module="$PWD/upstream_fair" \
%endif
%if %{with headers_more}
    --add-module="$PWD/headers_more" \
%endif
%if %{with balancer}
    --add-module="$PWD/balancer" \
%endif
%if %{with perl_module}
    --with-http_perl_module \
%endif
%if 0%{?with_gperftools}
    --with-google_perftools_module \
%endif
    --with-pcre \
    --with-ipv6 \
    --with-debug \
    --with-cc-opt="%{optflags} $(pcre-config --cflags)" \
    --with-ld-opt="$RPM_LD_FLAGS -Wl,-E" # so the perl module finds its symbols 
#    --add-module="$PWD/healthcheck" \
#    --add-module="$PWD/ngx_supervisord" \




make %{?_smp_mflags}

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot} INSTALLDIRS=vendor
find %{buildroot} -type f -name .packlist -exec rm -f {} \;
find %{buildroot} -type f -name perllocal.pod -exec rm -f {} \;
find %{buildroot} -type f -empty -exec rm -f {} \;
find %{buildroot} -type f -exec chmod 0644 {} \;
find %{buildroot} -type f -name '*.so' -exec chmod 0755 {} \;
chmod 0755 %{buildroot}%{_sbindir}/nginx
%{__install} -p -D -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
%{__install} -p -D -m 0644 %{SOURCE5} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_confdir}/conf.d
%{__install} -p -m 0644 %{SOURCE3} %{SOURCE4} %{buildroot}%{nginx_confdir}/conf.d
%{__install} -p -m 0644 %{SOURCE6} %{buildroot}%{nginx_confdir}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_home_tmp}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_logdir}
%{__install} -p -d -m 0755 %{buildroot}%{nginx_webroot}
%{__install} -p -m 0644 %{SOURCE100} %{SOURCE101} %{SOURCE102} %{SOURCE103} %{SOURCE104} %{buildroot}%{nginx_webroot}
cp -a nginx_custom_configs_htmlroot/srv %{buildroot}
cp -a nginx_custom_configs_htmlroot/etc %{buildroot}

# convert to UTF-8 all files that give warnings.
for textfile in CHANGES
do
    mv $textfile $textfile.old
    iconv --from-code ISO8859-1 --to-code UTF-8 --output $textfile $textfile.old
    rm -f $textfile.old
done


%clean
rm -rf %{buildroot}


%pre
if [ $1 == 1 ]; then
    %{_sbindir}/useradd -c "Nginx user" -s /bin/false -r -d %{nginx_home} %{nginx_user} 2>/dev/null || :
fi


%post
if [ $1 == 1 ]; then
    /sbin/chkconfig --add %{name}
fi


%preun
if [ $1 = 0 ]; then
    /sbin/service %{name} stop >/dev/null 2>&1
    /sbin/chkconfig --del %{name}
fi


%postun
if [ $1 == 2 ]; then
    /sbin/service %{name} upgrade || :
fi


%files
%defattr(-,root,root,-)
%doc LICENSE CHANGES README
%{nginx_datadir}/
%{_sbindir}/%{name}
%if %{with perl_module}
%{_mandir}/man3/%{name}.3pm.gz
%endif
%{_initrddir}/%{name}
%dir %{nginx_confdir}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_confdir}/conf.d
%dir %{nginx_confdir}/inc
%dir %{nginx_confdir}/pki
%dir %{nginx_confdir}/sites.d
%dir /srv
%dir %{nginx_logdir}
%config(noreplace) %{nginx_confdir}/conf.d/*.conf
%config(noreplace) %{nginx_confdir}/win-utf
%config(noreplace) %{nginx_confdir}/%{name}.conf.default
%config(noreplace) %{nginx_confdir}/mime.types.default
%config(noreplace) %{nginx_confdir}/fastcgi.conf
%config(noreplace) %{nginx_confdir}/fastcgi.conf.default
%config(noreplace) %{nginx_confdir}/fastcgi_params
%config(noreplace) %{nginx_confdir}/fastcgi_params.default
%config(noreplace) %{nginx_confdir}/scgi_params
%config(noreplace) %{nginx_confdir}/scgi_params.default
%config(noreplace) %{nginx_confdir}/uwsgi_params
%config(noreplace) %{nginx_confdir}/uwsgi_params.default
%config(noreplace) %{nginx_confdir}/koi-win
%config(noreplace) %{nginx_confdir}/koi-utf
%config(noreplace) %{nginx_confdir}/%{name}.conf
%config(noreplace) %{nginx_confdir}/mime.types
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%if %{with perl_module}
%dir %{perl_vendorarch}/auto/%{name}
%{perl_vendorarch}/%{name}.pm
%{perl_vendorarch}/auto/%{name}/%{name}.so
%endif
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home}
%attr(-,%{nginx_user},%{nginx_group}) %dir %{nginx_home_tmp}
%{nginx_confdir}/inc/*
%{nginx_confdir}/pki/*
%{nginx_confdir}/sites.d/*
%attr(-,%{nginx_user},%{nginx_group}) /srv/*


%changelog
* Thu May 9 2013  Stiliyan Sabchew <ssabchew at yahoo dot com> - 128:1.4.1-0.SS
- update to version 1.4.1 - CVE-2013-2028

* Thu May 9 2013  Stiliyan Sabchew <ssabchew at yahoo dot com> - 128:1.4.0-0.SS
- Update to version 1.4.0
- remove ustats module, due to build error
- remove extended_status module due to build error
- remove chunkin module as it is build-in now

* Tue Apr 30 2013 Stiliyan Sabchew <ssabchew at yahoo dot com> - 128:1.2.2-0.SS
- port for f18

* Thu Jul 26 2012 Stiliyan Sabchev <ssabchev at gmail dot com> - 128:1.2.2-0.SS
- Update to 1.2.2
- changed default upstream module from eybalancer to fair
- added extended_status module
- added ustats for default roundrobin module

* Wed Jun 20 2012  Stiliyan Sabchev <ssabchev at gmail dot com> - 128:1.2.1-0.SS 
- Update to 1.2.1

* Wed May 16 2012 Stiliyan Sabchew <ssabchew at yahoo dot com> - 128:1.2.0-0.SS
- update to 1.2.0
- added patch for ey-balancer module

* Mon Oct 10 2011 Stiliyan Sabchew <ssabchev at yahoo dot com> - 128:1.0.8-0.SS
- upgrade to 1.0.8
- added start_time patch

* Sat Jul 09 2011 Stiliyan Sabche  <ssabchew at yahoo dot com> - 128:1.0.0-2.SS
- Update to 1.0.0
- Increased upgrade time from 60 to 120 sec
- Changed epoch to 128

* Thu Feb 24 2011 Doncho N. Gunchev <dgunchev at gmail dot com> - 1:0.8.54-1.SS
- Made the build parametrized.
- Added headers-more module.

* Mon Nov 22 2010 Doncho N. Gunchev <dgunchev at gmail dot com> - 1:0.8.53-1.SS
- Removed perl parts
- Re-Added upstream-fair module
- Re-Added chunkin module
- Changed epoch to 1

* Sun Oct 31 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.8.53-1
- Update to new stable 0.8.53 since 0.6.x branch is no longer supported

* Sun Jun 20 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.39-5
- fix bug #591543

* Mon Feb 15 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.39-4
- change directory ownership of log dir to root:root

* Mon Feb 15 2010 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.39-3
- fix bug #554914 

* Fri Dec 04 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.39-2
- fixes CVE-2009-3555

* Mon Sep 14 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.39-1
- update to 0.6.39
- fixes CVE-2009-2629

* Sun Aug 02 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.38-1
- update to 0.6.38

* Sat Apr 11 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> 0.6.36-1
-  update to 0.6.36

* Thu Feb 19 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.35-2
- rebuild

* Thu Feb 19 2009 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.35-1
- update to 0.6.35

* Tue Dec 30 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.34-1
- update to 0.6.34
- Fix inclusion of /usr/share/nginx tree => no unowned directories [mschwendt]

* Sun Nov 23 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.33-1
- update to 0.6.33

* Sun Jul 27 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.32-1
- update to 0.6.32
- nginx now supports DESTDIR so removed the patches that enabled it

* Mon May 26 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.31-3
- update init script
- remove 'default' listen parameter

* Tue May 13 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.31-2
- added missing Source files

* Mon May 12 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.6.31-1
- update to new upstream stable branch 0.6
- added 3rd party module nginx-upstream-fair
- add /etc/nginx/conf.d support [#443280]
- use /etc/sysconfig/nginx to determine nginx.conf [#442708]
- added default webpages
- add Requires for versioned perl (libperl.so) (via Tom "spot" Callaway)
- drop silly file Requires (via Tom "spot" Callaway)

* Sat Jan 19 2008 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.5.35-1
- update to 0.5.35

* Sun Dec 16 2007 Jeremy Hinegardner <jeremy at hinegardner dot org> - 0.5.34-1
- update to 0.5.34

* Mon Nov 12 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.33-2
- bump build number - source wasn't update

* Mon Nov 12 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.33-1
* update to 0.5.33

* Mon Sep 24 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.32-1
- updated to 0.5.32
- fixed rpmlint UTF-8 complaints.

* Sat Aug 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.31-3
- added --with-http_stub_status_module build option.
- added --with-http_sub_module build option.
- add in pcre-config --cflags

* Sat Aug 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.31-2
- remove BuildRequires: perl-devel

* Fri Aug 17 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.31-1
- Update to 0.5.31
- specify license is BSD

* Sat Aug 11 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.30-2
- Add BuildRequires: perl-devel - fixing rawhide build

* Mon Jul 30 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.30-1
- Update to 0.5.30

* Tue Jul 24 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.29-1
- Update to 0.5.29

* Wed Jul 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.28-1
- Update to 0.5.28

* Mon Jul 09 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.27-1
- Update to 0.5.27

* Mon Jun 18 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.26-1
- Update to 0.5.26

* Sat Apr 28 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.19-1
- Update to 0.5.19

* Mon Apr 02 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.17-1
- Update to 0.5.17

* Mon Mar 26 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.16-1
- Update to 0.5.16
- add ownership of /usr/share/nginx/html (#233950)

* Fri Mar 23 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.15-3
- fixed package review bugs (#235222) given by ruben@rubenkerkhof.com

* Thu Mar 22 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.15-2
- fixed package review bugs (#233522) given by kevin@tummy.com

* Thu Mar 22 2007 Jeremy Hinegardner <jeremy@hinegardner.org> - 0.5.15-1
- create patches to assist with building for Fedora
- initial packaging for Fedora
